from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class JobWorkIssueWizard(models.TransientModel):
    _name = 'job.work.issue.wizard'
    _description = 'Job Work Issue Wizard'

    job_work_line_id = fields.Many2one('mrp.jobwork.line', string='Job Work Line', readonly=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    issued_qty = fields.Float('Quantity to Issue', required=True)
    expected_date = fields.Date('Expected Date')
    rate = fields.Float('Rate', required=True)
    amount = fields.Float(string="Total Amount", compute='_compute_amount', readonly=True)

    # Helper field to show user how much is available
    available_qty = fields.Float(string="Available Quantity", readonly=True)

    @api.depends('issued_qty', 'rate')
    def _compute_amount(self):
        for wizard in self:
            wizard.amount = wizard.issued_qty * wizard.rate

    def action_confirm(self):
        self.ensure_one()
        if self.issued_qty <= 0:
            raise ValidationError(_("Quantity to issue must be positive."))
        if self.issued_qty > self.available_qty:
            raise ValidationError(_("You cannot issue more than the available quantity of %s.", self.available_qty))

        self.env['job.work.issue.line'].create({
            'job_work_line_id': self.job_work_line_id.id,
            'vendor_id': self.vendor_id.id,
            'issued_qty': self.issued_qty,
            'expected_date': self.expected_date,
            'rate': self.rate,
        })
        return {'type': 'ir.actions.act_window_close'}


class JobWorkReceiptWizard(models.TransientModel):
    _name = 'job.work.receipt.wizard'
    _description = 'Job Work Receipt Wizard'

    job_work_line_id = fields.Many2one('mrp.jobwork.line', string='Job Work Line', readonly=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    received_qty = fields.Float('Quantity to Receive', required=True)
    receive_date = fields.Date('Receive Date', default=fields.Date.context_today, required=True)

    # Helper field to show user how much is pending from this vendor
    pending_from_vendor_qty = fields.Float(string="Pending from Vendor", readonly=True)
    vendor_domain = fields.Char(string="Vendor Domain",compute='_compute_vendor_domain')

    @api.depends('job_work_line_id')
    def _compute_vendor_domain(self):
        for record in self:
            issued_vendor_ids = [issue.vendor_id.id for issue in record.job_work_line_id.issued_to_vendor_ids]
            record.vendor_domain = [('id', 'in', list(issued_vendor_ids))]



    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id and self.job_work_line_id:
            issued = sum(
                self.job_work_line_id.issued_to_vendor_ids.filtered(lambda v: v.vendor_id == self.vendor_id).mapped(
                    'issued_qty'))
            received = sum(
                self.job_work_line_id.received_from_vendor_ids.filtered(lambda v: v.vendor_id == self.vendor_id).mapped(
                    'received_qty'))
            self.pending_from_vendor_qty = issued - received
        else:
            self.pending_from_vendor_qty = 0

    def action_confirm(self):
        self.ensure_one()
        if self.received_qty <= 0:
            raise ValidationError(_("Quantity to receive must be positive."))
        if self.received_qty > self.pending_from_vendor_qty:
            raise ValidationError(_("You cannot receive more than the pending quantity of %s from this vendor.",
                                    self.pending_from_vendor_qty))

        self.env['job.work.receipt.line'].create({
            'job_work_line_id': self.job_work_line_id.id,
            'vendor_id': self.vendor_id.id,
            'received_qty': self.received_qty,
            'receive_date': self.receive_date
        })
        return {'type': 'ir.actions.act_window_close'}
