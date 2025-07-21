from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")


class StockMove(models.Model):
    _inherit = "stock.move"

    purchase_order_line_id = fields.Many2one("purchase.order.line", string="Purchase Line")
