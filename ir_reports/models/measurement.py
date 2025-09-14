from odoo import models, fields, api

class MeasurementReport(models.Model):
    _name = "measurement.report"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'record.lock.mixin']

    name = fields.Char(string="Number", copy=False, required=True, index=True, readonly=1, default='New', tracking=True)
    date = fields.Date(string="Date", tracking=True)
    fabricator_name_id = fields.Many2one("res.partner", string="FABRICATOR NAME", tracking=True)
    stage_id = fields.Many2one("stage.master", string="STAGE", tracking=True)
    debit = fields.Char(string="DEBIT", tracking=True)
    qty = fields.Float(string="Qty", tracking=True)
    master_name_id = fields.Many2one("res.partner", string="Master NAME", tracking=True)
    product_id = fields.Many2one("product.product", string="Style NO", tracking=True)
    product_cat_id = fields.Many2one("product.category", string="MC", tracking=True)
    brand_id = fields.Many2one("brand.master", string="Brand", tracking=True)
    mrp = fields.Float(string="MRP", tracking=True)
    d_no = fields.Char(string="D.NO", tracking=True)
    party_id = fields.Many2one("res.partner", string="Party", tracking=True)
    status = fields.Char(string="Status", tracking=True)
    delivery_date = fields.Date(string="Delivery DATE", tracking=True)
    remark = fields.Char(string="Remark", tracking=True)
    remark1 = fields.Char(string="Remark-1", tracking=True)
    line_ids = fields.One2many("measurement.report.line", "measurement_id", string="Lines", tracking=True)
    route_id = fields.Many2one("measurement.route", string="Route", tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    color_id = fields.Many2one("color.master", string="Color", tracking=True)
    washing_item_id = fields.Many2one("washing.item", string="WASHING", tracking=True)
    vendor_name = fields.Char(string="WASHER Name")
    img = fields.Binary(string="Image")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_cat_id = self.product_id.categ_id.id
        self.brand_id = self.product_id.brand_id.id
        self.mrp = self.product_id.mrp
        self.d_no = self.product_id.design_no
        self.vendor_name = self.product_id.vendor_name
        self.color_id = self.product_id.color_id.id
        self.washing_item_id = self.product_id.washing_item_id.id


    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.line_ids:
            self.line_ids = [(5, 0, 0)]
        lines = []
        for line in self.route_id.line_ids:
            lines.append((0, 0, {
                'process_id': line.process_id.id,
                'tol': line.tol,
                'remark': line.remark,
                'size1': line.size1,
                'size2': line.size2,
                'size3': line.size3,
                'size4': line.size4,
                'size5': line.size5,
            }))
        self.line_ids = lines

    def _get_date_field(self):
        return "date"

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('measurement.report') or 'new'
        res = super().create(vals_list)
        return res

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'measurement.report'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.sudo().filtered(lambda l: l.is_readonly or l.is_invisible):
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
                [('report_type', '=', 'measurement.report'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.sudo().line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.sudo().field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if view_type == "list":
                        if field.is_invisible:
                            field_node.set("column_invisible", "1")
                    if view_type == "form":
                        if field.is_invisible:
                            if field.field_id.model == 'measurement.report.line':
                                field_node.set("column_invisible", "1")
                            else:
                                field_node.set("invisible", "1")
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

class MeasurementReportLine(models.Model):
    _name = "measurement.report.line"

    measurement_id = fields.Many2one("measurement.report", string="Measurement")
    process_id = fields.Many2one("measurement.process", string="Particular")
    tol = fields.Char(string="TOL")
    remark = fields.Char(string="Remark")
    size1 = fields.Char(string="Size1")
    year1 = fields.Char(string="Years1")
    year2 = fields.Char(string="Years2")
    year3 = fields.Char(string="Years3")
    size2 = fields.Char(string="Size2")
    year4 = fields.Char(string="Years4")
    year5 = fields.Char(string="Years5")
    year6 = fields.Char(string="Years6")
    size3 = fields.Char(string="Size3")
    year7 = fields.Char(string="Years7")
    year8 = fields.Char(string="Years8")
    year9 = fields.Char(string="Years9")
    size4 = fields.Char(string="Size4")
    year10 = fields.Char(string="Years10")
    year11 = fields.Char(string="Years11")
    year12 = fields.Char(string="Years12")
    size5 = fields.Char(string="Size5")
    year13 = fields.Char(string="Years13")
    year14 = fields.Char(string="Years14")
    year15 = fields.Char(string="Years15")
    note1 = fields.Char(string="Note-1")
    note2 = fields.Char(string="Note-2")

    report_date = fields.Date(related="measurement_id.date", store=True, string="Report Date")
    fabricator_name_id = fields.Many2one(
        related="measurement_id.fabricator_name_id",
        store=True,
        string="Fabricator Name"
    )
    stage_id = fields.Many2one(related="measurement_id.stage_id", store=True, string="Stage")
    product_cat_id = fields.Many2one(related="measurement_id.product_cat_id", store=True, string="MC")
    product_id = fields.Many2one(related="measurement_id.product_id", store=True, string="Style NO")
    brand_id = fields.Many2one(
        related="measurement_id.brand_id",
        store=True,
        string="Brand"
    )
    party_id = fields.Many2one(
        related="measurement_id.party_id",
        store=True,
        string="Party"
    )
    master_name_id = fields.Many2one(
        related="measurement_id.master_name_id",
        store=True,
        string="Party"
    )
    delivery_date = fields.Date(
        related="measurement_id.delivery_date",
        store=True,
        string="Delivery Date"
    )
    mrp = fields.Float(related="measurement_id.mrp", store=True, string="Mrp")


    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Measurement Report",
            "res_model": "measurement.report",
            "res_id": self.measurement_id.id,
            "domain": [("id", "=", self.measurement_id.id)],
            "view_mode": "form",
        }


class StageMaster(models.Model):
    _name = "stage.master"

    name = fields.Char(string="Name")