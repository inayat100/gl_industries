from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    pps_report_id = fields.Many2one("api.report.configration", string="PPS Report")
    measurement_report_id = fields.Many2one("api.report.configration", string="Measurement Report")
    quality_report_id = fields.Many2one("api.report.configration", string="Quality Report")