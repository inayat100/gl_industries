from odoo import models, fields, api

class ApiReportConfigration(models.Model):
    _inherit = "api.report.configration"

    @api.onchange('report_type')
    def _onchange_report_type_id(self):
         if self.report_type == 'job_order_report':
            report_id = self.env.ref("mrp_job_work_outsourcing.model_job_work_issue_line")
            self.report_id = report_id.id