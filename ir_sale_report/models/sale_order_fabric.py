from odoo import models, fields,api

class SalesOrderFabric(models.Model):
    _name = 'sales.order.fabric'
    _description = 'Sales Order Fabric'

    is_favorite = fields.Boolean(string="Favorite")
    header = fields.Char(string="HEADER")
    sl_no = fields.Char(string="SL NO")
    date = fields.Date(string="DATE")
    product_id = fields.Many2one('product.product', string="Product")
    sorts_no = fields.Char(string="SORT NO")
    image = fields.Binary(string="IMAGE", attachment=True)
    fabric_colour = fields.Char(string="FABRIC COLOUR")
    fabric_mill = fields.Char(string="FABRIC MILL")
    fabric_supplier = fields.Char(string="FABRIC SUPPLIER")
    qty = fields.Float(string="QTY")
    hanger_fabric = fields.Char( string="HANGER / FABRIC")
    weave = fields.Char(string="WEAVE")
    fabric_category_id = fields.Many2one("product.category", string="FABRIC CATEGORY")
    content = fields.Char(string="CONTENT")
    count = fields.Char(string="COUNT")
    construction = fields.Char(string="CONSTRUCTION")
    weight = fields.Char(string="WEIGHT")
    pantone_no = fields.Char(string="PANTONE NO")
    location_rack_no = fields.Char(string="LOCATION / RACK NO")
    merchant_1 = fields.Char(string="MERCHANT 1")
    merchant_2 = fields.Char(string="MERCHANT 2")
    buyer_name = fields.Char(string="BUYER NAME")
    category = fields.Char(string="CATEGORY")
    garment_development = fields.Char(string="GARMENT DEVELOPMENT")
    status = fields.Char(string="STATUS")
    status_date = fields.Date(string="STATUS DATE")
    remarks_1 = fields.Text(string="REMARKS 1")
    remarks_2 = fields.Text(string="REMARKS 2")
    remark_date = fields.Date(string="REMARK DATE")
    style_no = fields.Char(string="STYLE NO")
    development_image = fields.Binary(string="DEVELOPMENT IMAGE", attachment=True)
    col_1 = fields.Char(string="COL 1")
    col_2 = fields.Char(string="COL 2")
    col_3 = fields.Char(string="COL 3")
    col_4 = fields.Char(string="COL 4")
    col_5 = fields.Char(string="COL 5")
    col_6 = fields.Char(string="COL 6")
    col_7 = fields.Char(string="COL 7")
    col_8 = fields.Char(string="COL 8")
    col_9 = fields.Char(string="COL 9")
    col_10 = fields.Char(string="COL 10")
    col_11 = fields.Char(string="COL 11")
    col_12 = fields.Char(string="COL 12")


    @api.onchange('product_id')
    def _onchange_product(self):
        for line in self:
            line.count = line.product_id.po_number_count
            line.fabric_category_id = line.product_id.categ_id.id
            line.sorts_no = line.product_id.fabric_short_no
            line.fabric_colour = line.product_id.color_id.name
            line.image = line.product_id.product_img_1
            line.qty = line.product_id.fabric_qty
            line.weight = line.product_id.fabric_weight
            line.construction = line.product_id.fabric_contruction
            line.content = line.product_id.content_pentone
            line.pantone_no = line.product_id.content_pentone
            line.fabric_supplier = line.product_id.vendor_name
            line.col_1 = line.product_id.col_1
            line.col_2 = line.product_id.col_2
            line.col_3 = line.product_id.col_3
            line.col_4 = line.product_id.col_4
            line.col_5 = line.product_id.col_5
            line.col_6 = line.product_id.col_6

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search([('report_type', '=', 'sale_fabric'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
            if field.is_readonly:
                test_list.append(True)
            else:
                test_list.append(False)
            if field.is_invisible:
                test_list.append(True)
            else:
                test_list.append(False)
            if report_id.disable_create:
                test_list.append(True)
            else:
                test_list.append(False)
            if report_id.disable_delete:
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
            report_id = self.env['api.report.configration'].search([('report_type', '=', 'sale_fabric'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
            if report_id.disable_create:
                for node in arch.xpath("//form"):
                    node.set("create", "0")
            if report_id.disable_delete:
                for node in arch.xpath("//form"):
                    node.set("delete", "0")
        return arch, view
