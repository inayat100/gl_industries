from odoo import models, fields, api

document_type_list = [
    ('po_article', 'PO/ARTICLE'),
    ('pps', 'PPS'),
    ('lab_test', 'Lab Test'),
    ('photo_sample', 'Photo Sample'),
    ('fit_sample', 'FIT Sample'),
]

class PPSLab(models.Model):
    _name = "pps.lab"
    _inherit = "record.lock.mixin"

    name = fields.Char(string="Number", copy=False, required=True, index=True, readonly=1, default='New')
    date = fields.Date(string="Date")
    document_type = fields.Selection(document_type_list, string="Document type")
    party_id = fields.Many2one("res.partner", string="Party")
    po_no = fields.Char(string="PO NO")
    new_po_no = fields.Char(string="New PO NO")
    article_no = fields.Char(string="ARTICLE NO")
    article_url = fields.Char(string="ARTICLE URL")
    new_article_no = fields.Char(string="New ARTICLE NO")
    po_url = fields.Char(string="PO URL")
    color_id = fields.Many2one("color.master", string="Color")
    product_cat_id = fields.Many2one("product.category", string="MC")
    mrp = fields.Float(string="MRP")
    season_id = fields.Many2one("season.master", string="Season")
    machine_name = fields.Char(string="Machine Name")
    style_no = fields.Char(string="Style NO")
    remark = fields.Char(string="Remark")
    pps_lab_lines = fields.One2many("pps.lab.line", "pps_lab_id", string="Lines")
    route_id = fields.Many2one("pps.route", string="Route")
    brand_id = fields.Many2one("brand.master", string="Brand")
    receive_date = fields.Date(string="Receive Date")
    sending_date = fields.Date(string="Sending Date")

    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.pps_lab_lines:
            self.pps_lab_lines = [(5, 0, 0)]
        lines = []
        for line in self.route_id.line_ids:
            lines.append((0, 0, {
                'process_id': line.process_id.id,
                'col1': line.col1,
                'col2': line.col2,
                'col3': line.col3,
                'col4': line.col4,
                'remark1': line.remark,
            }))
        self.pps_lab_lines = lines

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('pps.lab') or 'new'
        res = super().create(vals_list)
        return res


class PPSLabLine(models.Model):
    _name = "pps.lab.line"

    pps_lab_id = fields.Many2one("pps.lab", string="PPS LAB")
    process_id = fields.Many2one('pps.process', string='Process', required=True)
    name = fields.Char(string="Description")
    col1 = fields.Char(string="Col-1")
    col2 = fields.Char(string="Col-2")
    col3 = fields.Char(string="Col-3")
    col4 = fields.Char(string="Col-4")
    detail = fields.Char(string="DETAIL")
    date = fields.Date(string="Date")
    remark1 = fields.Char(string="Remark-1")
    remark2 = fields.Char(string="Remark-2")
    remark3 = fields.Char(string="Remark-3")
    remark4 = fields.Char(string="Remark-4")

    parent_date = fields.Date(related="pps_lab_id.date", string="Date", store=True, readonly=True)
    document_type = fields.Selection(
        related="pps_lab_id.document_type", string="Document Type", store=True, readonly=True
    )
    party_id = fields.Many2one(
        "res.partner", related="pps_lab_id.party_id", string="Party", store=True, readonly=True
    )
    po_no = fields.Char(related="pps_lab_id.po_no", string="PO NO", store=True, readonly=True)
    new_po_no = fields.Char(related="pps_lab_id.new_po_no", string="New PO NO", store=True, readonly=True)
    article_no = fields.Char(related="pps_lab_id.article_no", string="ARTICLE NO", store=True, readonly=True)
    article_url = fields.Char(related="pps_lab_id.article_url", string="ARTICLE URL", store=True, readonly=True)
    new_article_no = fields.Char(related="pps_lab_id.new_article_no", string="New ARTICLE NO", store=True,
                                 readonly=True)
    po_url = fields.Char(related="pps_lab_id.po_url", string="PO URL", store=True, readonly=True)
    color_id = fields.Many2one("color.master", related="pps_lab_id.color_id", string="Color", store=True, readonly=True)
    product_cat_id = fields.Many2one("product.category", related="pps_lab_id.product_cat_id", string="MC", store=True,
                                     readonly=True)
    mrp = fields.Float(related="pps_lab_id.mrp", string="MRP", store=True, readonly=True)
    season_id = fields.Many2one("season.master", related="pps_lab_id.season_id", string="Season", store=True,
                                readonly=True)
    machine_name = fields.Char(related="pps_lab_id.machine_name", string="Machine Name", store=True, readonly=True)
    style_no = fields.Char(related="pps_lab_id.style_no", string="Style NO", store=True, readonly=True)
    remark = fields.Char(related="pps_lab_id.remark", string="Remark", store=True, readonly=True)
    route_id = fields.Many2one("pps.route", related="pps_lab_id.route_id", string="Route", store=True, readonly=True)

    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "PPS Report",
            "res_model": "pps.lab",
            "res_id": self.pps_lab_id.id,
            "domain": [("id", "=", self.pps_lab_id.id)],
            "view_mode": "form",
        }



