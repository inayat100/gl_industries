from odoo import models, fields, api

class BomRoute(models.Model):
    _name = "bom.route"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    product_id = fields.Many2one("product.product", string="Product")
    product_cat_id = fields.Many2one("product.category", string="MC")
    mrp = fields.Float(string="MRP")
    party_id = fields.Many2one("res.partner", string="Party")
    qty = fields.Float(string="Qty")
    line_ids = fields.One2many("bom.route.line", "route_id", string="Lines")
    date = fields.Date(string="Date", default=fields.date.today())
    active = fields.Boolean(string="Active", default=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_cat_id = self.product_id.categ_id.id
        self.mrp = self.product_id.mrp



class BomRouteLine(models.Model):
    _name = "bom.route.line"

    route_id = fields.Many2one("bom.route", string="Route")
    product_id = fields.Many2one("product.product", string="Product")
    note = fields.Char(string="Note")
    uom_id = fields.Many2one("uom.uom", string="UOM")
    qty = fields.Float(string="Qty")
    qty_per_pack = fields.Float(string="Qty Per Pack")
    qty_percent = fields.Float(string="Qty percent")
    extra_per = fields.Float(string="Extra Per")
    rate = fields.Float(string="Rate")
    amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
    qty_in_pack = fields.Float(string="Qty In Pack")
    color_id = fields.Many2one("color.master", string="Color")
    size_id = fields.Many2one("size.master", string="Size")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    remark = fields.Char(string="Remark")

    @api.depends('rate', 'qty')
    def _compute_amount(self):
        for res in self:
            res.amount = res.qty * res.rate


    @api.onchange('product_id', 'extra_per', 'qty_in_pack', 'route_id.qty')
    def _onchange_qty(self):
        if self.qty_in_pack > 0:
            qty_per_pack = self.route_id.qty / self.qty_in_pack
        else:
            qty_per_pack = 0.0
        qty_percent = (qty_per_pack * self.extra_per) / 100
        self.qty_per_pack = qty_per_pack
        self.qty_percent = qty_percent
        self.qty = qty_per_pack + qty_percent


    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.uom_id = self.product_id.uom_id.id
        self.rate = self.product_id.standard_price
        self.qty_in_pack = self.product_id.qty_in_pack
        self.color_id = self.product_id.color_id.id
        self.size_id = self.product_id.size_id.id