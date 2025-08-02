from odoo import fields, models, api


class ProductionPlaning(models.Model):
    _name = 'production.planing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production Planing'

    is_favorite = fields.Boolean(string="Favorite", tracking=True)
    date = fields.Date(string='Date', tracking=True)
    fabric_vendor_id = fields.Many2one('res.partner', string='Fabric Vendor', tracking=True)
    product_id = fields.Many2one("product.product", string='Sort No', tracking=True)
    fabric_item = fields.Char(string='Fabric Item', tracking=True)
    fabric_colour_id = fields.Many2one("color.master", string='Fabric Colour', tracking=True)
    qty = fields.Float(string='Qty', tracking=True)
    style_no = fields.Char(string='Style No', tracking=True)
    party_id = fields.Many2one('res.partner', string='Party', tracking=True)
    product_cat_id = fields.Many2one('product.category', string='MC', tracking=True)
    status = fields.Char(string='Status', tracking=True)
    file_received_date = fields.Date(string='File Received Date', tracking=True)
    cutting_master_id = fields.Many2one("res.partner", string='Cutting Master', tracking=True)
    blanket = fields.Char(string='Blanket', tracking=True)
    blanket_status = fields.Char(string='Blanket Status', tracking=True)
    shrinkage_sample = fields.Char(string='Shrinkage Sample', tracking=True)
    pattern = fields.Char(string='Pattern', tracking=True)
    remark = fields.Char(string='Remark', tracking=True)
    cutting_start_date = fields.Date(string='Cutting Start Date', tracking=True)
    cutting_end_date = fields.Date(string='Cutting End Date', tracking=True)
    vendor_id = fields.Many2one("res.partner", string='Fabricator Name', tracking=True)
    location = fields.Char(string='Location', tracking=True)
    total_machines = fields.Integer(string='Total Machines', tracking=True)
    heavy_machines = fields.Integer(string='Heavy Machines', tracking=True)
    garment_design = fields.Text(string='Garment Design', tracking=True)
    plan_date = fields.Date(string='Plan Date', tracking=True)
    no_of_person = fields.Integer(string='No of Person', tracking=True)
    no_of_qc_person = fields.Integer(string='No of Person by QC', tracking=True)
    no_of_style = fields.Integer(string='No of Style', tracking=True)
    total_qty = fields.Float(string='Total Qty', tracking=True)
    status_by_qc = fields.Char(string='Status by QC', tracking=True)
    status_date = fields.Date(string='Status Date', tracking=True)
    qc_status = fields.Html(string="Status", tracking=True)
    next_week_remark = fields.Char(string='Remark', tracking=True)
    required_qty_vendor = fields.Char(string='Required Qty Vendor', tracking=True)
    next_week_plan = fields.Char(string='Next Week Planning', tracking=True)
    next_week_qty = fields.Float(string='Next Week Qty', tracking=True)

    # Additional columns you mentioned
    short_no = fields.Char(string='Fabric Short No', tracking=True)
    fabric_qty = fields.Float(string='Fabric Qty', tracking=True)
    purchase_order_no = fields.Char(string='Purchase Order No', tracking=True)
    sample = fields.Char(string='Sample', tracking=True)
    labtest = fields.Char(string='Labtest', tracking=True)
    pps = fields.Char(string='PPS', tracking=True)

    col_1 = fields.Char(string='Col-1', tracking=True)
    col_2 = fields.Char(string='Col-2', tracking=True)
    col_3 = fields.Char(string='Col-3', tracking=True)
    col_4 = fields.Char(string='Col-4')
    col_5 = fields.Char(string='Col-5', tracking=True)
    col_6 = fields.Char(string='Col-6', tracking=True)
    col_7 = fields.Char(string='Col-7', tracking=True)
    col_8 = fields.Char(string='Col-8', tracking=True)
    col_9 = fields.Char(string='Col-9', tracking=True)
    col_10 = fields.Char(string='Col-10', tracking=True)
    col_11 = fields.Char(string='Col-11', tracking=True)
    col_12 = fields.Char(string='Col-12', tracking=True)
    col_13 = fields.Char(string='Col-13', tracking=True)
    col_14 = fields.Char(string='Col-14', tracking=True)
    note_1 = fields.Char(string='Note-1', tracking=True)
    note_2 = fields.Char(string='Note-2', tracking=True)
    note_3 = fields.Char(string='Note-3', tracking=True)
    note_4 = fields.Char(string='Note-4', tracking=True)
    note_5 = fields.Char(string='Note-5', tracking=True)
    note_6 = fields.Char(string='Note-6', tracking=True)
    note_7 = fields.Char(string='Note-7', tracking=True)
    note_8 = fields.Char(string='Note-8', tracking=True)
    note_9 = fields.Char(string='Note-9', tracking=True)
    note_10 = fields.Char(string='Note-10', tracking=True)
    note_11 = fields.Char(string='Note-11', tracking=True)
    note_12 = fields.Char(string='Note-12', tracking=True)
    note_13 = fields.Char(string='Note-13', tracking=True)
    note_14 = fields.Char(string='Note-14', tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Production Planing Reports",
            "res_model": "production.planing",
            "res_id": self.id,
            "domain": [("id", "=", self.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False},
        }



    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.pps = self.product_id.pps_width
        self.product_cat_id = self.product_id.categ_id.id
        self.short_no = self.product_id.fabric_short_no
        self.labtest = self.product_id.lab_comp

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'production_planning'), ('user_id', '=', self.env.user.id)], limit=1)
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
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'production_planning'), ('user_id', '=', self.env.user.id)], limit=1)
        if view_type == "list":
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
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