from odoo import models, fields, api

model_name_list = [
        ('quality.report', 'Quality Report'),
        ('pps.lab', 'PPS Lab'),
        ('measurement.report', 'Measurement Report'),
        ('sale.order', 'Sale Order'),
        ('purchase.order', 'Purchase Order'),
        ('mrp.production', 'Manufacturing Order'),
    ]

class RecordLockConfig(models.Model):
    _name = "record.lock.config"
    _description = "Record Lock Configuration"

    model_name = fields.Selection(model_name_list, string="Model", required=True)
    date_field_id = fields.Many2one(
        'ir.model.fields',
        string="Date Field",
        domain="[('ttype', 'in', ('date', 'datetime')), ('model', '=', model_name)]",
        required=True,
        ondelete="cascade",
        help="Select the date/datetime field used for validation"
    )
    base_on_date = fields.Boolean(string="Base On Date")

    lock_create_before_day = fields.Integer(string="Disallow Create Before")
    lock_edit_before_day = fields.Integer(string="Disallow Edit Before")
    lock_delete_before_day = fields.Integer(string="Disallow Delete Before")

    lock_create_after_day = fields.Integer(string="Disallow Create After")
    lock_edit_after_day = fields.Integer(string="Disallow Edit After")
    lock_delete_after_day = fields.Integer(string="Disallow Delete After")

    lock_create_before = fields.Date("Disallow Create Before")
    lock_edit_before = fields.Date("Disallow Edit Before")
    lock_delete_before = fields.Date("Disallow Delete Before")

    lock_create_after = fields.Date("Disallow Create After")
    lock_edit_after = fields.Date("Disallow Edit After")
    lock_delete_after = fields.Date("Disallow Delete After")

    _sql_constraints = [
        ('unique_model', 'unique(model_name)', "Configuration for this model already exists!"),
    ]