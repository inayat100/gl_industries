from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    bom_report_id = fields.Many2one("api.report.configration", string="BOM Report")
    bom_line_report_id = fields.Many2one("api.report.configration", string="BOM Line Report")