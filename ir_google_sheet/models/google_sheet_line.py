from odoo import models, fields, _

class GoogleSheetLine(models.Model):
    _name = "google.sheet.line"
    _rec_name = "field_name"
    _description = "Google Sheet Line"

    google_sheet_id = fields.Many2one("google.sheet", string="Google Sheet", ondelete="cascade")
    domain_type = fields.Selection([
        ('name', 'Name'),
        ('number', 'Number'),
    ], string="Domain Type")
    field_name = fields.Char(string="Field Name")
    field_head = fields.Char(string="Head Name")
    field_style = fields.Char(string="Style")
    col_name = fields.Char(string="Col Name")
    add_sheet = fields.Boolean(string="Add")
    is_formula = fields.Boolean(string="Is Formula")
    formula = fields.Char(string="Formula")

