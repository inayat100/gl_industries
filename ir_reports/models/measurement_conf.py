# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MeasurementProcess(models.Model):
    _name = 'measurement.process'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Measurement Process'
    _order = 'id'

    name = fields.Char('Process Name', required=True, tracking=True)
    description = fields.Text('Description', tracking=True)




class MeasurementRoute(models.Model):
    _name = 'measurement.route'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Measurement Route'

    name = fields.Char('Route Name', required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Custoomer")
    line_ids = fields.One2many('measurement.route.line', 'measurement_id', string='Process Lines', copy=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        for route in self:
            route.display_name = f"{route.name} [{route.partner_id.name}]" if route.partner_id and route.name else route.name



class MeasurementRouteLine(models.Model):
    _name = 'measurement.route.line'
    _description = 'Measurement Route Line'
    _order = 'sequence, id'

    measurement_id = fields.Many2one('measurement.route', string='Measurement Route', required=True, ondelete='cascade')
    process_id = fields.Many2one('measurement.process', string='Process', required=True)
    sequence = fields.Integer('Sequence', required=True, default=10)
    tol = fields.Char(string="TOL")
    size1 = fields.Char(string="Size-1")
    size2 = fields.Char(string="Size-2")
    size3 = fields.Char(string="Size-3")
    size4 = fields.Char(string="Size-4")
    size5 = fields.Char(string="Size-5")
    remark = fields.Char(string="Remark")
