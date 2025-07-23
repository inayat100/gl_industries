from odoo import fields, models, api


class SamplePlaning(models.Model):
    _name = "sample.planing"

    is_favorite = fields.Boolean(string="Favorite")
    product_id = fields.Many2one("product.product", string="Product")
    buyer_id = fields.Many2one("res.partner", string="Party")
    product_cat_id = fields.Many2one("product.category", string="MC")
    mrp = fields.Float(string="Mrp")
    spec = fields.Char(string="SPEC")
    fabric = fields.Char(string="Fabric")
    fabric_supplier_id = fields.Many2one("res.partner", string="Fabric Supplier")
    washing_id = fields.Many2one("res.partner", string="Washing")
    washing = fields.Char( string="Washing")
    merchant_id = fields.Many2one("res.partner", string="Merchant")
    merchant_comment = fields.Char( string="Merchant Comment")
    merchant_1_comment = fields.Char( string="Merchant-1 Comment")
    image_1 = fields.Binary(string="Image")
    image_2 = fields.Binary(string="Image")
    spc_pfd = fields.Char(string="SPCPFD")
    tec_pack = fields.Char(string="Tec pack")
    ref = fields.Char(string="Referance")
    sample_qty = fields.Float(string="Sample QTY")
    status = fields.Char(string="Status")
    status_date = fields.Date(string="Status Date")
    delivery_date = fields.Date(string="Delivery Date")
    col_1 = fields.Char(string="Col-1")
    col_2 = fields.Char(string="Col-2")
    col_3 = fields.Char(string="Col-3")
    col_4 = fields.Char(string="Col-4")
    col_5 = fields.Date(string="Col-5")
    col_6 = fields.Date(string="Col-6")
    fabric_book_date = fields.Date(string="Fabric Book")
    fabric_received_date = fields.Date(string="Fabric Received")
    fabric_received_status = fields.Char(string="Status")

    trims_book_date = fields.Date(string="Trims Book")
    trims_received_date = fields.Date(string="Trims Received")
    trims_received_status = fields.Char(string="Status")

    trims_1_book_date = fields.Date(string="Trims-1 Book")
    trims_1_received_date = fields.Date(string="Trims-1 Received")
    trims_1_received_status = fields.Char(string="Status")

    trims_2_book_date = fields.Date(string="Trims-2 Book")
    trims_2_received_date = fields.Date(string="Trims-2 Received")
    trims_2_received_status = fields.Char(string="Status")

    trims_3_book_date = fields.Date(string="Trims-3 Book")
    trims_3_received_date = fields.Date(string="Trims-3 Received")
    trims_3_received_status = fields.Char(string="Status")

    trims_4_book_date = fields.Date(string="Trims-4 Book")
    trims_4_received_date = fields.Date(string="Trims-4 Received")
    trims_4_received_status = fields.Char(string="Status")

    cutting_book_date = fields.Date(string="Cutting Book")
    cutting_received_date = fields.Date(string="Cutting Received")
    cutting_received_status = fields.Char(string="Status")

    stitching_book_date = fields.Date(string="Stitching Book")
    stitching_received_date = fields.Date(string="Stitching Received")
    stitching_received_status = fields.Char(string="Status")

    print_book_date = fields.Date(string="Printing Book")
    print_received_date = fields.Date(string="Printing Received")
    print_received_status = fields.Char(string="Status")

    emb_book_date = fields.Date(string="Emb Book")
    emb_received_date = fields.Date(string="Emb Received")
    emb_received_status = fields.Char(string="Status")

    washing_book_date = fields.Date(string="Washing Book")
    washing_received_date = fields.Date(string="Washing Received")
    washing_received_status = fields.Char(string="Status")

    finishing_book_date = fields.Date(string="Finishing Book")
    finishing_received_date = fields.Date(string="Finishing Received")
    finishing_received_status = fields.Char(string="Status")

    packing_book_date = fields.Date(string="Packing Book")
    packing_received_date = fields.Date(string="Packing Received")
    packing_received_status = fields.Char(string="Status")

    delivery_book_date = fields.Date(string="Delivery Book")
    delivery_received_date = fields.Date(string="Delivery Received")
    delivery_received_status = fields.Char(string="Status")

    @api.onchange('product_id')
    def _onchange_product_id_method(self):
        self.mrp = self.product_id.mrp
        self.product_cat_id = self.product_id.categ_id.id
        self.image_1 = self.product_id.image_1920
        self.image_2 = self.product_id.product_img_1
        self.spc_pfd = self.product_id

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'sample_planning'), ('user_id', '=', self.env.user.id)], limit=1)
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
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'sample_planning'), ('user_id', '=', self.env.user.id)], limit=1)
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


