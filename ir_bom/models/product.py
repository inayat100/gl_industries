from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_in_pack = fields.Float(string="Qty In Pack")