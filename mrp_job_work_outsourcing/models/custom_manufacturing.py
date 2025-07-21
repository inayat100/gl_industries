# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    job_work_route_id = fields.Many2one('job.work.route', string='Job Work Route', tracking=True)
    jobwork_line_ids = fields.One2many('mrp.jobwork.line', 'mo_id', string='Job Work Lines')

    jobwork_issue_count = fields.Integer(compute='_compute_jobwork_counts')
    jobwork_receipt_count = fields.Integer(compute='_compute_jobwork_counts')
    total_job_work_days = fields.Integer(string="Total Job Work Days", compute='_compute_job_work_dates', store=True, readonly=True)
    job_work_expected_date = fields.Date(string="Job Work Expected Date", compute='_compute_job_work_dates', store=True, readonly=True)

    @api.depends('jobwork_line_ids.days_to_complete', 'date_start')
    def _compute_job_work_dates(self):
        for mo in self:
            total_days = sum(mo.jobwork_line_ids.mapped('days_to_complete'))
            mo.total_job_work_days = total_days
            if mo.date_start and total_days > 0:
                mo.job_work_expected_date = mo.date_start + timedelta(days=total_days)
            else:
                mo.job_work_expected_date = False

    def _compute_jobwork_counts(self):
        for mo in self:
            mo.jobwork_issue_count = len(self.env['job.work.issue.line'].search([('mo_id', '=', mo.id)]))
            mo.jobwork_receipt_count = len(self.env['job.work.receipt.line'].search([('mo_id', '=', mo.id)]))

    @api.onchange('job_work_route_id')
    def _onchange_job_work_route_id(self):
        if not self.job_work_route_id:
            self.jobwork_line_ids = [(5, 0, 0)]  # Remove all lines
            return

        lines_to_create = []
        for route_line in self.job_work_route_id.line_ids:
            lines_to_create.append((0, 0, {
                'process_id': route_line.process_id.id,
                'sequence': route_line.sequence,
                'rate': route_line.rate,
                'days_to_complete': route_line.days_to_complete,
            }))

        self.jobwork_line_ids = [(5, 0, 0)]  # Clear existing lines first
        self.jobwork_line_ids = lines_to_create

    # def get_available_qty_for_process(self, process_sequence):
    #     """
    #     Calculates the quantity available for a given process.
    #     For the first process, it's the MO quantity.
    #     For subsequent processes, it's the received quantity of the previous process.
    #     """
    #     self.ensure_one()
    #     if process_sequence == 1:
    #         return self.product_qty
    #
    #     previous_process_line = self.jobwork_line_ids.filtered(lambda l: l.sequence == process_sequence - 1)
    #     if not previous_process_line:
    #         # This might happen if sequences are not contiguous, find the next lowest
    #         previous_process_line = self.jobwork_line_ids.sorted('sequence', reverse=True).filtered(
    #             lambda l: l.sequence < process_sequence)
    #         if not previous_process_line:
    #             return 0  # Should not happen in a normal flow
    #         previous_process_line = previous_process_line[0]
    #
    #     return previous_process_line.received_qty

    def get_available_qty_for_process(self, process_sequence):
        """
        Calculates the quantity available for a given process sequence.
        For the first process in the route, it's the MO quantity.
        For subsequent processes, it's the received quantity of the previous process.
        """
        self.ensure_one()

        # Get all lines sorted by sequence
        all_lines = self.jobwork_line_ids.sorted('sequence')

        print('All lines',all_lines)

        if not all_lines:
            return 0

        # Check if the given sequence belongs to the first process in the route
        if process_sequence == all_lines[0].sequence:
            return self.product_qty

        # Find all processes with a sequence number lower than the current one
        previous_lines = all_lines.filtered(lambda l: l.sequence < process_sequence)

        if not previous_lines:
            # This is a safeguard. If no previous lines are found, it cannot proceed.
            return 0

        # The immediately preceding process is the last one in the filtered & sorted list
        previous_process_line = previous_lines[-1]

        return previous_process_line.received_qty

    def action_view_jobwork_issues(self):
        self.ensure_one()
        return {
            'name': _('Job Work Issues'),
            'type': 'ir.actions.act_window',
            'res_model': 'job.work.issue.line',
            'view_mode': 'list,form',
            'domain': [('mo_id', '=', self.id)],
            'context': {'default_mo_id': self.id}
        }

    def action_view_jobwork_receipts(self):
        self.ensure_one()
        return {
            'name': _('Job Work Receipts'),
            'type': 'ir.actions.act_window',
            'res_model': 'job.work.receipt.line',
            'view_mode': 'list,form',
            'domain': [('mo_id', '=', self.id)],
            'context': {'default_mo_id': self.id}
        }




