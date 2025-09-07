from odoo import models, fields, api

class QualityReport(models.Model):
    _name = "quality.report"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'record.lock.mixin']

    name = fields.Char(string="Number", copy=False, required=True, index=True, readonly=1, default='New', tracking=True)
    date = fields.Date(string="Date", tracking=True)
    fabricator_name_id = fields.Many2one("res.partner", string="FABRICATOR NAME", tracking=True)
    location = fields.Char(string="Location", tracking=True)
    product_id = fields.Many2one("product.product", string="STYLE NO", tracking=True)
    product_cat_id = fields.Many2one("product.category", string="MC", tracking=True)
    qty = fields.Float(string="QTY", tracking=True)
    cutting_issue_date = fields.Date(string="CUTTING ISSUE DATE", tracking=True)
    brand_id = fields.Many2one("brand.master", string="Brand", tracking=True)
    cutting_remark = fields.Char(string="Cutting Problem", tracking=True)
    seller_sample = fields.Char(string="Seller Sample", tracking=True)
    no_of_operator = fields.Char(string=" NO OF Operator", tracking=True)
    status = fields.Char(string="Status", tracking=True)
    remark = fields.Char(string="Remark", tracking=True)
    delivery_date = fields.Date(string="Delivery DATE", tracking=True)
    trims_lines = fields.One2many("quality.report.trims", "quality_id", string="Trims")
    trims_route_id = fields.Many2one("quality.route", string="Route")
    sewing_machine_lines = fields.One2many("quality.report.sewing.machine", "quality_id", string="Sewing")
    sewing_route_id = fields.Many2one("quality.route", string="Route")
    feed_lines = fields.One2many("quality.report.feed.off.machine", "quality_id", string="Feed")
    feed_route_id = fields.Many2one("quality.route", string="Route")
    construction_lines = fields.One2many("quality.report.construction", "quality_id", string="Construction")
    construction_route_id = fields.Many2one("quality.route", string="Route")
    active = fields.Boolean(string="Active", default=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_cat_id = self.product_id.categ_id.id
        self.brand_id = self.product_id.brand_id.id

    @api.onchange('trims_route_id')
    def _onchange_trims_route_id(self):
        if self.trims_lines:
            self.trims_lines = [(5, 0, 0)]
        lines = []
        for line in self.trims_route_id.line_ids:
            lines.append((0, 0, {
                'process_id': line.process_id.id,
                'process_remark': line.remark
            }))
        self.trims_lines = lines

    @api.onchange('sewing_route_id')
    def _onchange_sewing_route_id(self):
        if self.sewing_machine_lines:
            self.sewing_machine_lines = [(5, 0, 0)]
        lines = []
        for line in self.sewing_route_id.line_ids:
            lines.append((0, 0, {
                'process_id': line.process_id.id,
                'process_remark': line.remark
            }))
        self.sewing_machine_lines = lines

    @api.onchange('feed_route_id')
    def _onchange_feed_route_id(self):
        if self.feed_lines:
            self.feed_lines = [(5, 0, 0)]
        lines = []
        for line in self.feed_route_id.line_ids:
            lines.append((0, 0, {
                'process_id': line.process_id.id,
                'process_remark': line.remark
            }))
        self.feed_lines = lines

    @api.onchange('construction_route_id')
    def _onchange_construction_route_id(self):
        if self.construction_lines:
            self.construction_lines = [(5, 0, 0)]
        lines = []
        for line in self.construction_route_id.line_ids:
            lines.append((0, 0, {
                'process_id': line.process_id.id,
                'process_remark': line.remark
            }))
        self.construction_lines = lines

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('quality.report') or 'new'
        res = super().create(vals_list)
        return res

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'quality.report'), ('user_id', '=', self.env.user.id)], limit=1)
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
                [('report_type', '=', 'quality.report'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.sudo().line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.sudo().field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if view_type == "list":
                        if field.is_invisible:
                            field_node.set("column_invisible", "1")
                    if view_type == "form":
                        if field.is_invisible:
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


class QualityReportTrims(models.Model):
    _name = "quality.report.trims"
    _description = "Trims"

    process_id = fields.Many2one('quality.process', string='Process')
    process_remark = fields.Char(string="Process Remark")
    quality_id = fields.Many2one("quality.report", string="Quality")
    fabricator_name_id = fields.Many2one(related="quality_id.fabricator_name_id", store=True, string="FABRICATOR NAME")
    product_qt_id = fields.Many2one(related="quality_id.product_id", store=True, string="STYLE NO")
    product_qt_cat_id = fields.Many2one(related="quality_id.product_cat_id", store=True, string="MC")
    qty = fields.Float(related="quality_id.qty", store=True, string="QTY")
    route_id = fields.Many2one(related="quality_id.trims_route_id", store=True, string="Route")
    product_id = fields.Many2one("product.product", string="Product")
    receive = fields.Char(string="Receive")
    product_cat_id = fields.Many2one("product.category", string="MC")
    remark = fields.Char(string="Remark")
    remark1 = fields.Char(string="Remark1")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_cat_id = self.product_id.categ_id.id

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Quality Reports",
            "res_model": "quality.report",
            "res_id": self.quality_id.id,
            "domain": [("id", "=", self.quality_id.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False, 'delete': False},
        }



class QualityReportSewingMachine(models.Model):
    _name = "quality.report.sewing.machine"
    _description = "Sewing Machine"

    process_id = fields.Many2one('quality.process', string='Process')
    process_remark = fields.Char(string="Process Remark")
    quality_id = fields.Many2one("quality.report", string="Quality")
    machine_name = fields.Char(string="Machine Name")
    machine_no = fields.Char(string="Machine No")
    operator_name = fields.Char(string="Operator NAME")
    spi = fields.Char(string="SPI")
    roll_no = fields.Char(string="Roll NO")
    remark = fields.Char(string="Remark")
    remark1 = fields.Char(string="Remark1")
    fabricator_name_id = fields.Many2one(related="quality_id.fabricator_name_id", store=True, string="FABRICATOR NAME")
    product_qt_id = fields.Many2one(related="quality_id.product_id", store=True, string="STYLE NO")
    product_qt_cat_id = fields.Many2one(related="quality_id.product_cat_id", store=True, string="MC")
    qty = fields.Float(related="quality_id.qty", store=True, string="QTY")
    route_id = fields.Many2one(related="quality_id.sewing_route_id", store=True, string="Route")

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Quality Reports",
            "res_model": "quality.report",
            "res_id": self.quality_id.id,
            "domain": [("id", "=", self.quality_id.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False, 'delete': False},
        }


class QualityReportFeedOffMachine(models.Model):
    _name = "quality.report.feed.off.machine"
    _description = "Feed Off Machine"

    process_id = fields.Many2one('quality.process', string='Process')
    process_remark = fields.Char(string="Process Remark")
    quality_id = fields.Many2one("quality.report", string="Quality")
    machine_name = fields.Char(string="Machine Name")
    machine_no = fields.Char(string="Machine No")
    operator_name = fields.Char(string="Operator NAME")
    spi = fields.Char(string="SPI")
    roll_no = fields.Char(string="Roll NO")
    remark = fields.Char(string="Remark")
    remark1 = fields.Char(string="Remark1")

    fabricator_name_id = fields.Many2one(related="quality_id.fabricator_name_id", store=True, string="FABRICATOR NAME")
    product_qt_id = fields.Many2one(related="quality_id.product_id", store=True, string="STYLE NO")
    product_qt_cat_id = fields.Many2one(related="quality_id.product_cat_id", store=True, string="MC")
    qty = fields.Float(related="quality_id.qty", store=True, string="QTY")
    route_id = fields.Many2one(related="quality_id.feed_route_id", store=True, string="Route")

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Quality Reports",
            "res_model": "quality.report",
            "res_id": self.quality_id.id,
            "domain": [("id", "=", self.quality_id.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False, 'delete': False},
        }


class QualityReportConstruction(models.Model):
    _name = "quality.report.construction"
    _description = "Construction"

    process_id = fields.Many2one('quality.process', string='Process')
    process_remark = fields.Char(string="Process Remark")
    quality_id = fields.Many2one("quality.report", string="Quality")
    position = fields.Char(string="Position")
    operator_name = fields.Char(string="Operator NAME")
    roll_no = fields.Char(string="Roll NO")
    remark = fields.Char(string="Remark")
    remark1 = fields.Char(string="Remark1")
