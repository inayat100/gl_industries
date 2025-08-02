from odoo import models, fields,api

class SalesOrderFabric(models.Model):
    _name = 'sales.order.fabric'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Order Fabric'

    is_favorite = fields.Boolean(string="Favorite", tracking=True)
    header = fields.Char(string="HEADER", tracking=True)
    sl_no = fields.Char(string="SL NO", tracking=True)
    date = fields.Date(string="DATE", tracking=True)
    product_id = fields.Many2one('product.product', string="Product", tracking=True)
    sorts_no = fields.Char(string="SORT NO", tracking=True)
    image = fields.Binary(string="IMAGE")
    fabric_colour_id = fields.Many2one("color.master", string="FABRIC COLOUR", tracking=True)
    fabric_mill = fields.Char(string="FABRIC MILL", tracking=True)
    vendor_id = fields.Many2one("res.partner", string="FABRIC SUPPLIER", tracking=True)
    qty = fields.Float(string="QTY", tracking=True)
    hanger_fabric = fields.Char( string="HANGER / FABRIC", tracking=True)
    fit_measurement_id = fields.Many2one("fit.measurement", string="WEAVE", tracking=True)
    fabric_category_id = fields.Many2one("product.category", string="FABRIC CATEGORY", tracking=True)
    content = fields.Char(string="CONTENT", tracking=True)
    count = fields.Char(string="COUNT", tracking=True)
    construction = fields.Char(string="CONSTRUCTION", tracking=True)
    weight = fields.Char(string="WEIGHT")
    pantone_no = fields.Char(string="PANTONE NO", tracking=True)
    location_rack_no = fields.Char(string="LOCATION / RACK NO", tracking=True)
    merchant_id = fields.Many2one("res.users", string="MERCHANT 1", tracking=True)
    merchant_2 = fields.Char(string="MERCHANT 2", tracking=True)
    party_id = fields.Many2one("res.partner", string="BUYER NAME", tracking=True)
    product_cat_id = fields.Many2one("product.category", string="CATEGORY", tracking=True)
    garment_development = fields.Char(string="GARMENT DEVELOPMENT", tracking=True)
    status = fields.Char(string="STATUS", tracking=True)
    status_date = fields.Date(string="STATUS DATE", tracking=True)
    remarks_1 = fields.Text(string="REMARKS 1", tracking=True)
    remarks_2 = fields.Text(string="REMARKS 2", tracking=True)
    remark_date = fields.Date(string="REMARK DATE", tracking=True)
    style_no = fields.Char(string="STYLE NO", tracking=True)
    development_image = fields.Binary(string="DEVELOPMENT IMAGE", attachment=True)
    col_1 = fields.Char(string="COL 1", tracking=True)
    col_2 = fields.Char(string="COL 2", tracking=True)
    col_3 = fields.Char(string="COL 3", tracking=True)
    col_4 = fields.Char(string="COL 4", tracking=True)
    col_5 = fields.Char(string="COL 5", tracking=True)
    col_6 = fields.Char(string="COL 6", tracking=True)
    col_7 = fields.Char(string="COL 7", tracking=True)
    col_8 = fields.Char(string="COL 8", tracking=True)
    col_9 = fields.Char(string="COL 9", tracking=True)
    col_10 = fields.Char(string="COL 10", tracking=True)
    col_11 = fields.Char(string="COL 11", tracking=True)
    col_12 = fields.Char(string="COL 12", tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Fabric YARDAGE Reports",
            "res_model": "sales.order.fabric",
            "res_id": self.id,
            "domain": [("id", "=", self.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False},
        }


    @api.onchange('product_id')
    def _onchange_product(self):
        for line in self:
            line.product_cat_id = line.product_id.categ_id.id
            line.count = line.product_id.po_number_count
            line.fit_measurement_id = line.product_id.fit_measurement_id.id
            line.fabric_category_id = line.product_id.categ_id.id
            line.sorts_no = line.product_id.fabric_short_no
            line.fabric_colour_id = line.product_id.color_id.id
            line.image = line.product_id.image_1920
            line.qty = line.product_id.fabric_qty
            line.weight = line.product_id.fabric_weight
            line.construction = line.product_id.fabric_contruction
            line.content = line.product_id.content_pentone
            line.pantone_no = line.product_id.content_pentone
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
        if report_id.disable_edit:
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
            if report_id.disable_edit:
                for node in arch.xpath("//form"):
                    node.set("edit", "0")
        return arch, view
