from odoo import models, fields, _, api

class GoogleSheetLine(models.Model):
    _name = "google.sheet.line"
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
    is_sum = fields.Boolean("Is Sum")
    is_formula = fields.Boolean(string="Is Formula")
    formula = fields.Char(string="Formula")

    @api.depends('field_name', 'col_name')
    def _compute_display_name(self):
        for res in self:
            name = res.field_name
            if res.col_name:
                name = f"{name}-[{res.col_name}]"
            res.display_name = name

