from odoo import fields, models, api
from odoo.exceptions import UserError


class SamplePlaning(models.Model):
    _name = "sample.planing"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string="Date")
    is_favorite = fields.Boolean(string="Favorite")
    product_id = fields.Many2one("product.product", string="Product", tracking=True)
    party_id = fields.Many2one("res.partner", string="Party", tracking=True)
    product_cat_id = fields.Many2one("product.category", string="MC", tracking=True)
    mrp = fields.Float(string="Mrp", tracking=True)
    spec = fields.Char(string="SPEC", tracking=True)
    fabric = fields.Char(string="Fabric", tracking=True)
    vendor_id = fields.Many2one("res.partner", string="Fabric Supplier", tracking=True)
    washing_id = fields.Many2one("res.partner", string="Washing", tracking=True)
    washing = fields.Char( string="Washing", tracking=True)
    merchant_id = fields.Many2one("res.users", string="Merchant", tracking=True)
    merchant_comment = fields.Char( string="Merchant Comment", tracking=True)
    merchant_1_comment = fields.Char( string="Merchant-1 Comment", tracking=True)
    image_1 = fields.Binary(string="Image")
    image_2 = fields.Binary(string="Image")
    spc_pfd = fields.Char(string="SPCPFD", tracking=True)
    tec_pack = fields.Char(string="Tec pack", tracking=True)
    ref = fields.Char(string="Referance", tracking=True)
    sample_qty = fields.Float(string="Sample QTY", tracking=True)
    status = fields.Char(string="Status", tracking=True)
    status_date = fields.Date(string="Status Date", tracking=True)
    delivery_date = fields.Date(string="Delivery Date", tracking=True)
    col_1 = fields.Char(string="Col-1", tracking=True)
    col_2 = fields.Char(string="Col-2", tracking=True)
    col_3 = fields.Char(string="Col-3", tracking=True)
    col_4 = fields.Char(string="Col-4", tracking=True)
    col_5 = fields.Date(string="Col-5", tracking=True)
    col_6 = fields.Date(string="Col-6", tracking=True)
    fabric_book_date = fields.Date(string="Fabric Book", tracking=True)
    fabric_received_date = fields.Date(string="Fabric Received", tracking=True)
    fabric_received_status = fields.Char(string="Status", tracking=True)

    trims_book_date = fields.Date(string="Trims Book", tracking=True)
    trims_received_date = fields.Date(string="Trims Received", tracking=True)
    trims_received_status = fields.Char(string="Status", tracking=True)

    trims_1_book_date = fields.Date(string="Trims-1 Book", tracking=True)
    trims_1_received_date = fields.Date(string="Trims-1 Received", tracking=True)
    trims_1_received_status = fields.Char(string="Status", tracking=True)

    trims_2_book_date = fields.Date(string="Trims-2 Book", tracking=True)
    trims_2_received_date = fields.Date(string="Trims-2 Received", tracking=True)
    trims_2_received_status = fields.Char(string="Status", tracking=True)

    trims_3_book_date = fields.Date(string="Trims-3 Book", tracking=True)
    trims_3_received_date = fields.Date(string="Trims-3 Received", tracking=True)
    trims_3_received_status = fields.Char(string="Status", tracking=True)

    trims_4_book_date = fields.Date(string="Trims-4 Book", tracking=True)
    trims_4_received_date = fields.Date(string="Trims-4 Received", tracking=True)
    trims_4_received_status = fields.Char(string="Status", tracking=True)

    cutting_book_date = fields.Date(string="Cutting Book", tracking=True)
    cutting_received_date = fields.Date(string="Cutting Received", tracking=True)
    cutting_received_status = fields.Char(string="Status", tracking=True)

    stitching_book_date = fields.Date(string="Stitching Book", tracking=True)
    stitching_received_date = fields.Date(string="Stitching Received", tracking=True)
    stitching_received_status = fields.Char(string="Status", tracking=True)

    print_book_date = fields.Date(string="Printing Book", tracking=True)
    print_received_date = fields.Date(string="Printing Received", tracking=True)
    print_received_status = fields.Char(string="Status", tracking=True)

    emb_book_date = fields.Date(string="Emb Book", tracking=True)
    emb_received_date = fields.Date(string="Emb Received", tracking=True)
    emb_received_status = fields.Char(string="Status", tracking=True)

    washing_book_date = fields.Date(string="Washing Book", tracking=True)
    washing_received_date = fields.Date(string="Washing Received", tracking=True)
    washing_received_status = fields.Char(string="Status", tracking=True)

    finishing_book_date = fields.Date(string="Finishing Book", tracking=True)
    finishing_received_date = fields.Date(string="Finishing Received", tracking=True)
    finishing_received_status = fields.Char(string="Status", tracking=True)

    packing_book_date = fields.Date(string="Packing Book", tracking=True)
    packing_received_date = fields.Date(string="Packing Received", tracking=True)
    packing_received_status = fields.Char(string="Status", tracking=True)

    delivery_book_date = fields.Date(string="Delivery Book", tracking=True)
    delivery_received_date = fields.Date(string="Delivery Received", tracking=True)
    delivery_received_status = fields.Char(string="Status", tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Sample Planing Reports",
            "res_model": "sample.planing",
            "res_id": self.id,
            "domain": [("id", "=", self.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False},
        }

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
        for field in report_id.sudo().line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
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
        if view_type in ["list", "form"]:
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'sample_planning'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.sudo().line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.sudo().field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
            if report_id.disable_create:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("create", "0")
            if report_id.disable_delete:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("delete", "0")
            if report_id.disable_edit:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("edit", "0")
        return arch, view


    def copy(self, default=None):
        report_id = self.env['api.report.configration'].search([('report_type', '=', 'sample_planning'), ('user_id', '=', self.env.user.id)], limit=1)
        if report_id and report_id.disable_duplicate:
            raise UserError("You are not allowed to duplicate, as duplication is restricted.")
        res = super().copy(default)
        return res

    def toggle_active(self):
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'sample_planning'), ('user_id', '=', self.env.user.id)], limit=1)
        if report_id and report_id.disable_archive:
            raise UserError("You are not allowed to archive or unarchive this record.")
        return super().toggle_active()


