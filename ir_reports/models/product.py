from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    stage_id = fields.Many2one("stage.master", string="STAGE", tracking=True)