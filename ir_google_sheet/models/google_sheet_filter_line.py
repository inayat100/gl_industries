from odoo import models, fields, _
from odoo.exceptions import UserError



class GoogleSheetFilterLine(models.Model):
    _name = "google.sheet.filter.line"
    _description = "Google Sheet Filter Line"
    _order = "id"

    google_sheet_id = fields.Many2one(
        "google.sheet",
        string="Google Sheet",
        required=True,
        ondelete="cascade"
    )
    sheet_line_id = fields.Many2one(
        "google.sheet.line",
        string="Field",
        required=True,
        domain="[('domain_type', '=', domain_type), ('google_sheet_id', '=', google_sheet_id)]"
    )

    domain_type = fields.Selection([
        ('name', 'Name'),
        ('number', 'Number'),
    ], string="Domain Type")

    operator = fields.Selection([
        ('=', 'Equals'),
        ('!=', 'Not Equals'),
        ('contains', 'Contains'),
        ('not_contains', 'Does Not Contain'),
    ], string="Text Operator")

    number_operator = fields.Selection([
        ('=', 'Equals'),
        ('!=', 'Not Equals'),
        ('>', 'Greater Than'),
        ('<', 'Less Than'),
        ('>=', 'Greater Than Or Equal'),
        ('<=', 'Less Than Or Equal'),
    ], string="Number Operator")

    value_text = fields.Char(string="Text Value")
    value_number = fields.Float(string="Number Value")

    suggested_value_ids = fields.Many2many(
        "google.sheet.filter.value",
        string="Suggested Value",
        domain="[('domain_type', '=', domain_type), ('google_sheet_id', '=', google_sheet_id), ('sheet_line_id', '=', sheet_line_id)]"
    )

    active = fields.Boolean(default=True)

    # @api.onchange('suggested_value_id')
    # def _onchange_suggested_value_id(self):
    #     for rec in self:
    #         if rec.suggested_value_id and rec.domain_type == 'name':
    #             rec.value_text = rec.suggested_value_id.name




class GoogleSheetFilterValue(models.Model):
    _name = "google.sheet.filter.value"
    _description = "Google Sheet Filter Value"
    _order = "field_name, name"

    name = fields.Char(string="Value", required=True)
    google_sheet_id = fields.Many2one(
        "google.sheet",
        string="Google Sheet",
        required=True,
        ondelete="cascade"
    )
    sheet_line_id = fields.Many2one(
        "google.sheet.line",
        string="Sheet Field",
        required=True,
        ondelete="cascade"
    )
    field_name = fields.Char(string="Field Name", required=True)
    domain_type = fields.Selection([
        ('name', 'Name'),
        ('number', 'Number'),
    ], string="Domain Type", required=True)

    _sql_constraints = [
        (
            'google_sheet_field_value_unique',
            'unique(google_sheet_id, sheet_line_id, name, domain_type)',
            'Suggested value must be unique per field.'
        )
    ]