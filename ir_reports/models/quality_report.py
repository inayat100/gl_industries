from odoo import models, fields, api

class QualityReport(models.Model):
    _name = "quality.report"
    _inherit = "record.lock.mixin"

    name = fields.Char(string="Number", copy=False, required=True, index=True, readonly=1, default='New')
    date = fields.Date(string="Date")
    fabricator_name_id = fields.Many2one("res.partner", string="FABRICATOR NAME")
    location = fields.Char(string="Location")
    product_id = fields.Many2one("product.product", string="STYLE NO")
    product_cat_id = fields.Many2one("product.category", string="MC")
    qty = fields.Float(string="QTY")
    cutting_issue_date = fields.Date(string="CUTTING ISSUE DATE")
    brand_id = fields.Many2one("brand.master", string="Brand")
    cutting_remark = fields.Char(string="Cutting Problem")
    seller_sample = fields.Char(string="Seller Sample")
    no_of_operator = fields.Char(string=" NO OF Operator")
    status = fields.Char(string="Status")
    remark = fields.Char(string="Remark")
    delivery_date = fields.Date(string="Delivery DATE")
    trims_lines = fields.One2many("quality.report.trims", "quality_id", string="Trims")
    trims_route_id = fields.Many2one("quality.route", string="Route")
    sewing_machine_lines = fields.One2many("quality.report.sewing.machine", "quality_id", string="Sewing")
    sewing_route_id = fields.Many2one("quality.route", string="Route")
    feed_lines = fields.One2many("quality.report.feed.off.machine", "quality_id", string="Feed")
    feed_route_id = fields.Many2one("quality.route", string="Route")
    construction_lines = fields.One2many("quality.report.construction", "quality_id", string="Construction")
    construction_route_id = fields.Many2one("quality.route", string="Route")

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


class QualityReportTrims(models.Model):
    _name = "quality.report.trims"
    _description = "Trims"

    process_id = fields.Many2one('quality.process', string='Process')
    process_remark = fields.Char(string="Process Remark")
    quality_id = fields.Many2one("quality.report", string="Quality")
    product_id = fields.Many2one("product.product", string="Product")
    receive = fields.Char(string="Receive")
    product_cat_id = fields.Many2one("product.category", string="MC")
    remark = fields.Char(string="Remark")
    remark1 = fields.Char(string="Remark1")


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
