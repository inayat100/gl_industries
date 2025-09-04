from odoo import models, fields, api, _
from odoo.exceptions import UserError

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
    user_id = fields.Many2one("res.users", string="User", copy=False)
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

    @api.constrains('model_name', 'user_id')
    def _check_unique_user_model(self):
        for record in self:
            if record.user_id:
                for user in record.user_id:
                    duplicate = self.search([
                        ('id', '!=', record.id),
                        ('model_name', '=', record.model_name),
                        ('user_id', '=', user.id)
                    ], limit=1)
                    if duplicate:
                        raise UserError(_(
                            "User '%s' is already assigned to model '%s'. "
                            "Duplicate entries are not allowed."
                        ) % (user.name, record.model_name))