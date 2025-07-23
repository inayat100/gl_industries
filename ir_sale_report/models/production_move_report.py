from odoo import models, fields, api


class ProductionMoveReport(models.Model):
    _name = "production.move.report"
    _description = "Production Move Report"
    _auto = False

    id = fields.Many2one("stock.move", string="SM", readonly=1)
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
    in_qty = fields.Float(string="In Qty", readonly=1)
    po_date = fields.Datetime(string="PO Date")
    so_date = fields.Datetime(string="SO Date")
    picking_date = fields.Datetime(string="Picking Date")

    p_remark_1 = fields.Char(string="P Remark1")
    p_remark_2 = fields.Char(string="P Remark2")
    p_remark_3 = fields.Char(string="P Remark3")
    p_remark_4 = fields.Char(string="P Remark4")

    c_remark_1 = fields.Char(string="C Remark1")
    c_remark_2 = fields.Char(string="C Remark2")
    c_remark_3 = fields.Char(string="C Remark3")
    c_remark_4 = fields.Char(string="C Remark4")

    product_cat_id = fields.Many2one("product.category", string="MC")
    mrp = fields.Float(string="MRP")
    brand_id = fields.Many2one("brand.master", string="Branch")


    def _query(self):
        qry = """
        select sm.id as "id", sm.id as "stock_move_id", mp.id as "mo_id", so.id as "sale_id", pol.id as "purchase_line_id", mp.product_id as "product_id", sm.product_id as "bom_product_id", sol.product_uom_qty as "so_qty", pol.product_qty as "po_qty",
        so.partner_id as "so_partner_id", po.partner_id as "po_partner_id", psm.quantity as "in_qty", po.date_order as "po_date", so.date_order as "so_date", sp.scheduled_date as "picking_date",
        po.remark_1 as "p_remark_1", po.remark_2 as "p_remark_2", po.remark_3 as "p_remark_3", po.remark_4 as "p_remark_4",
        sm.remark_1 as "c_remark_1", sm.remark_2 as "c_remark_2", sm.remark_3 as "c_remark_3", sm.remark_4 as "c_remark_4",
		pt.categ_id as "product_cat_id", pt.brand_id as "brand_id", pt.mrp as "mrp"
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
        LEFT JOIN stock_move psm
        ON pol.id = psm.purchase_line_id
        LEFT JOIN stock_picking sp
        ON psm.picking_id = sp.id
        LEFT JOIN stock_picking_type spt
        ON sp.picking_type_id = spt.id
		LEFT JOIN product_product pp
		ON mp.product_id = pp.id
		LEFT JOIN product_template pt
		ON pp.product_tmpl_id = pt.id
        where sm.raw_material_production_id IS NOT NULL
        AND (
            sp.picking_type_id IS NULL
            OR (sp.picking_type_id IS NOT NULL AND spt.code = 'incoming')
            )

        """
        return qry

    @property
    def _table_query(self):
        return self._query()

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'component_report'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
            if field.is_invisible:
                test_list.append(True)
            else:
                test_list.append(False)
        test_list = tuple(test_list)
        key = key + (
            test_list,
        )
        return key

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "list":
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'component_report'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
        return arch, view


