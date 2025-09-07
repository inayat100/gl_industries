# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta



class MrpJobWorkLine(models.Model):
    _name = 'mrp.jobwork.line'
    _description = 'Manufacturing Job Work Line'
    _order = 'sequence, id'

    mo_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, ondelete='cascade')
    process_id = fields.Many2one('job.work.process', string='Process', required=True)
    sequence = fields.Integer('Sequence', required=True)
    location = fields.Char(string='Work Location')

    total_qty_issued = fields.Float('Total Issued Qty', compute='_compute_quantities', store=True, readonly=True)
    received_qty = fields.Float('Total Received Qty', compute='_compute_quantities', store=True, readonly=True)
    pending_qty = fields.Float('Pending Qty', compute='_compute_quantities', store=True, readonly=True)

    rate = fields.Float('Rate')
    total_amount = fields.Float('Total Amount', compute='_compute_total_amount', store=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending_previous', 'Pending Previous Process'),
        ('ready', 'Ready to Issue'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', compute='_compute_status', store=True, default='draft')

    issued_to_vendor_ids = fields.One2many('job.work.issue.line', 'job_work_line_id', string='Issued to Vendors')
    received_from_vendor_ids = fields.One2many('job.work.receipt.line', 'job_work_line_id',
                                               string='Received from Vendors')

    available_to_issue_qty = fields.Float(string="Available to Issue", compute="_compute_available_to_issue")
    days_to_complete = fields.Integer('Days to Complete')
    expected_date = fields.Date('Expected Date', compute='_compute_expected_date', store=True, readonly=True)


    @api.depends('sequence', 'days_to_complete', 'mo_id.date_start', 'mo_id.jobwork_line_ids.days_to_complete')
    def _compute_expected_date(self):
        # This logic ensures that dates are calculated sequentially for all lines of an MO at once
        for mo in self.mapped('mo_id'):
            start_date = mo.date_start or fields.Date.context_today(self)
            cumulative_days = 0
            for line in mo.jobwork_line_ids.sorted('sequence'):
                cumulative_days += line.days_to_complete
                line.expected_date = start_date + timedelta(days=cumulative_days)


    @api.depends('mo_id', 'sequence', 'mo_id.jobwork_line_ids.received_qty')
    def _compute_available_to_issue(self):
        for line in self:
            available_qty = line.mo_id.get_available_qty_for_process(line.sequence)
            line.available_to_issue_qty = available_qty - line.total_qty_issued

    @api.depends('issued_to_vendor_ids.issued_qty', 'received_from_vendor_ids.received_qty')
    def _compute_quantities(self):
        for line in self:
            line.total_qty_issued = sum(line.issued_to_vendor_ids.mapped('issued_qty'))
            line.received_qty = sum(line.received_from_vendor_ids.mapped('received_qty'))
            line.pending_qty = line.total_qty_issued - line.received_qty

    @api.depends('issued_to_vendor_ids.amount')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = sum(line.issued_to_vendor_ids.mapped('amount'))

    @api.depends('total_qty_issued', 'received_qty', 'mo_id.product_qty', 'sequence','available_to_issue_qty')
    def _compute_status(self):
        for line in self:
            available_qty = line.mo_id.get_available_qty_for_process(line.sequence)

            if available_qty == 0 and line.sequence > 1:
                line.status = 'pending_previous'
            elif line.total_qty_issued == 0:
                line.status = 'ready'
            elif line.total_qty_issued > 0 and line.received_qty < line.total_qty_issued:
                line.status = 'in_progress'
            elif line.total_qty_issued > 0 and line.received_qty == line.total_qty_issued:
                line.status = 'done'
            else:
                line.status = 'draft'

    def action_open_record(self):
        """
        This method is called by the 'Open' button on the tree view.
        It returns an action that opens the form view of the current record.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.jobwork.line',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_open_issue_wizard(self):
        self.ensure_one()
        issued_vendor_ids = [issue.vendor_id.id for issue in self.issued_to_vendor_ids]
        return {
            'name': _('Issue Material to Vendor'),
            'type': 'ir.actions.act_window',
            'res_model': 'job.work.issue.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_job_work_line_id': self.id,
                'default_available_qty': self.available_to_issue_qty,
                'default_vendor_domain': [('id', 'in', list(issued_vendor_ids))],
                'default_rate': self.rate,
            }
        }

    def action_open_receipt_wizard(self):
        self.ensure_one()
        # Get vendors to whom material has been issued but not fully received
        issued_vendors = self.issued_to_vendor_ids.filtered(lambda i: i.issued_qty > i.received_qty).mapped('vendor_id')
        return {
            'name': _('Receive Material from Vendor'),
            'type': 'ir.actions.act_window',
            'res_model': 'job.work.receipt.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_job_work_line_id': self.id,
                # Pass the domain for the vendor field in the wizard
                'vendor_domain': [('id', 'in', issued_vendors.ids)]
            }
        }


# ----------------------------------------
# Job Work Issue Line (to Vendor)
# ----------------------------------------
class JobWorkIssueLine(models.Model):
    _name = 'job.work.issue.line'
    _description = 'Job Work Issue to Vendor'

    job_work_line_id = fields.Many2one('mrp.jobwork.line', string='Job Work', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    issued_qty = fields.Float('Issued Quantity', required=True)
    received_qty = fields.Float('Received Quantity', compute='_compute_received_qty', store=True)
    issue_date = fields.Date('Issue Date', default=fields.Date.context_today, required=True)
    user_issue_date = fields.Date('User Entry Date')
    expected_date = fields.Date('Expected Date')
    days_to_complete = fields.Integer(related="job_work_line_id.days_to_complete", store=True)
    rate = fields.Float('Rate', required=True)
    amount = fields.Float('Amount', compute='_compute_amount', store=True)
    pending_qty = fields.Float('Pending Quantity', compute='_compute_received_qty', store=True)
    status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('done', 'Completed')
    ], string='Status', compute='_compute_received_qty', store=True)
    last_receipt_date = fields.Date(string="Last Received Date", compute='_compute_received_qty', store=True)
    remarks = fields.Text('Remarks')
    remark_1 = fields.Text('Remark 1')
    remark_2 = fields.Text('Remark 2')
    remark_3 = fields.Text('Remark 3')
    remark_date = fields.Date("Remark Date")

    # Related fields for easier access and reporting
    mo_id = fields.Many2one(related='job_work_line_id.mo_id', store=True, readonly=True)
    bom_id = fields.Many2one(related='job_work_line_id.mo_id.bom_id', store=True, readonly=True)
    job_work_expected_date = fields.Date(related='job_work_line_id.mo_id.job_work_expected_date', store=True, readonly=True)
    date_start = fields.Datetime(related='job_work_line_id.mo_id.date_start', store=True, readonly=True)
    product_qty = fields.Float(related='job_work_line_id.mo_id.product_qty', store=True, readonly=True)
    product_id = fields.Many2one(related='job_work_line_id.mo_id.product_id', store=True, readonly=True)
    categ_id = fields.Many2one(related='job_work_line_id.mo_id.product_id.categ_id', store=True, readonly=True)
    mrp = fields.Float(related='job_work_line_id.mo_id.product_id.mrp', store=True, readonly=True)
    brand_id = fields.Many2one(related='job_work_line_id.mo_id.product_id.brand_id', store=True, readonly=True)
    process_id = fields.Many2one(related='job_work_line_id.process_id', store=True, readonly=True)

    @api.depends('job_work_line_id.received_from_vendor_ids.received_qty', 'issued_qty')
    def _compute_received_qty(self):
        for issue in self:
            # Find all receipts for this issue's vendor and process
            receipts = self.env['job.work.receipt.line'].search([
                ('job_work_line_id', '=', issue.job_work_line_id.id),
                ('vendor_id', '=', issue.vendor_id.id)
            ])

            total_received = sum(receipts.mapped('received_qty'))

            # Find the total issued to this vendor for this process
            total_issued = sum(issue.job_work_line_id.issued_to_vendor_ids.filtered(
                lambda i: i.vendor_id == issue.vendor_id
            ).mapped('issued_qty'))

            issue.received_qty = total_received

            pending = total_issued - total_received
            issue.pending_qty = pending if pending > 0 else 0

            if issue.pending_qty > 0:
                issue.status = 'in_progress'
            else:
                issue.status = 'done'

            if receipts:
                # Find the maximum (most recent) date from the receipts
                issue.last_receipt_date = max(receipts.mapped('receive_date'))
            else:
                issue.last_receipt_date = False

    @api.depends('issued_qty', 'rate')
    def _compute_amount(self):
        for issue in self:
            issue.amount = issue.issued_qty * issue.rate

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'job_order_report'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
            if field.is_invisible:
                test_list.append(True)
            else:
                test_list.append(False)
        test_list = tuple(test_list)
        key = key + (
            test_list,
        )
        return key

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "list":
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'job_order_report'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
        return arch, view

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "MO",
            "res_model": "mrp.production",
            "res_id": self.mo_id.id,
            "domain": [("id", "=", self.mo_id.id)],
            "view_mode": "form",
        }




# ----------------------------------------
# Job Work Receipt Line (from Vendor)
# ----------------------------------------
class JobWorkReceiptLine(models.Model):
    _name = 'job.work.receipt.line'
    _description = 'Job Work Receipt from Vendor'

    job_work_line_id = fields.Many2one('mrp.jobwork.line', string='Job Work', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    received_qty = fields.Float('Received Quantity', required=True)
    receive_date = fields.Date('Receive Date', default=fields.Date.context_today, required=True)

    # Related fields for easier access and reporting
    mo_id = fields.Many2one(related='job_work_line_id.mo_id', store=True, readonly=True)
    process_id = fields.Many2one(related='job_work_line_id.process_id', store=True, readonly=True)

    @api.constrains('received_qty')
    def _check_received_qty(self):
        for line in self:
            job_line = line.job_work_line_id

            # Total issued to this specific vendor for this process
            total_issued_to_vendor = sum(job_line.issued_to_vendor_ids.filtered(
                lambda i: i.vendor_id == line.vendor_id
            ).mapped('issued_qty'))

            # Total received from this specific vendor for this process
            total_received_from_vendor = sum(job_line.received_from_vendor_ids.filtered(
                lambda r: r.vendor_id == line.vendor_id
            ).mapped('received_qty'))

            if total_received_from_vendor > total_issued_to_vendor:
                raise ValidationError(_(
                    "Cannot receive a total of %(received)s from vendor '%(vendor)s' for process '%(process)s'. "
                    "Only %(issued)s was issued to them.",
                    received=total_received_from_vendor,
                    vendor=line.vendor_id.name,
                    process=job_line.process_id.name,
                    issued=total_issued_to_vendor
                ))
