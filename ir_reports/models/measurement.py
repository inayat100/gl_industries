from odoo import models, fields, api

class MeasurementReport(models.Model):
    _name = "measurement.report"
    _inherit = "record.lock.mixin"

    name = fields.Char(string="Number", copy=False, required=True, index=True, readonly=1, default='New')
    date = fields.Date(string="Date")
    fabricator_name_id = fields.Many2one("res.partner", string="FABRICATOR NAME")
    stage_id = fields.Many2one("stage.master", string="STAGE")
    debit = fields.Char(string="DEBIT")
    qty = fields.Float(string="Qty")
    master_name_id = fields.Many2one("res.partner", string="Master NAME")
    style_no = fields.Char(string="Style NO")
    product_cat_id = fields.Many2one("product.category", string="MC")
    brand_id = fields.Many2one("brand.master", string="Brand")
    mrp = fields.Float(string="MRP")
    d_no = fields.Char(string="D.NO")
    party_id = fields.Many2one("res.partner", string="Party")
    status = fields.Char(string="Status")
    delivery_date = fields.Date(string="Delivery DATE")
    remark = fields.Char(string="Remark")
    remark1 = fields.Char(string="Remark-1")
    line_ids = fields.One2many("measurement.report.line", "measurement_id", string="Lines")
    route_id = fields.Many2one("measurement.route", string="Route")

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


class MeasurementReportLine(models.Model):
    _name = "measurement.report.line"

    measurement_id = fields.Many2one("measurement.report", string="Measurement")
    process_id = fields.Many2one("measurement.process", string="Particular")
    tol = fields.Char(string="TOL")
    remark = fields.Char(string="Remark")
    size1 = fields.Char(string="Size1")
    year1 = fields.Char(string="Years")
    year2 = fields.Char(string="Years")
    year3 = fields.Char(string="Years")
    size2 = fields.Char(string="Size2")
    year4 = fields.Char(string="Years")
    year5 = fields.Char(string="Years")
    year6 = fields.Char(string="Years")
    size3 = fields.Char(string="Size3")
    year7 = fields.Char(string="Years")
    year8 = fields.Char(string="Years")
    year9 = fields.Char(string="Years")
    size4 = fields.Char(string="Size4")
    year10 = fields.Char(string="Years")
    year11 = fields.Char(string="Years")
    year12 = fields.Char(string="Years")
    size5 = fields.Char(string="Size5")
    year13 = fields.Char(string="Years")
    year14 = fields.Char(string="Years")
    year15 = fields.Char(string="Years")
    note1 = fields.Char(string="Note-1")
    note2 = fields.Char(string="Note-2")

    report_date = fields.Date(related="measurement_id.date", store=True, string="Report Date")
    fabricator_name_id = fields.Many2one(
        related="measurement_id.fabricator_name_id",
        store=True,
        string="Fabricator Name"
    )
    stage_id = fields.Many2one(related="measurement_id.stage_id", store=True, string="Stage")
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
    delivery_date = fields.Date(
        related="measurement_id.delivery_date",
        store=True,
        string="Delivery Date"
    )


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