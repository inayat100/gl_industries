from odoo import models, fields, api


class ProductionMoveReport(models.Model):
    _name = "production.move.report"
    _description = "Production Move Report"
    _auto = False

    id = fields.Many2one("mrp.production", string="MO", readonly=1)
    mo_id = fields.Many2one("mrp.production", string="MO", readonly=1)
    stock_move_id = fields.Many2one("stock.move", string="Move", readonly=1)
    sale_id = fields.Many2one("sale.order", string="Sale Order", readonly=1)
    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase Line", readonly=1)
    bom_product_id = fields.Many2one("product.product", string="Component Product", readonly=1)
    product_id = fields.Many2one("product.product", string="Product", readonly=1)
    so_partner_id = fields.Many2one("res.partner", string="Customer", readonly=1)
    po_partner_id = fields.Many2one("res.partner", string="Vendor", readonly=1)
    so_qty = fields.Float(string="SO QTY", readonly=1)
    po_qty = fields.Float(string="PO QTY", readonly=1)

    def _query(self):
        qry = """
        select sm.id as "id", sm.id as "stock_move_id", mp.id as "mo_id", so.id as "sale_id", pol.id as "purchase_line_id", mp.product_id as "product_id", sm.product_id as "bom_product_id", sol.product_uom_qty as "so_qty", pol.product_qty as "po_qty",
        so.partner_id as "so_partner_id", po.partner_id as "po_partner_id"
        from stock_move sm
        LEFT JOIN mrp_production mp
        ON sm.raw_material_production_id = mp.id
        LEFT JOIN sale_order so
        ON mp.sale_order_id = so.id
        LEFT JOIN sale_order_line sol
        ON so.id = sol.order_id
        LEFT JOIN purchase_order_line pol
        ON sm.purchase_order_line_id = pol.id
        LEFT JOIN purchase_order po
        ON pol.order_id = po.id
        where sm.raw_material_production_id is not null 
        """
        return qry
    @property
    def _table_query(self):
        return self._query()
