# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MeasurementProcess(models.Model):
    _name = 'measurement.process'
    _description = 'Measurement Process'
    _order = 'id'

    name = fields.Char('Process Name', required=True)
    description = fields.Text('Description')




class MeasurementRoute(models.Model):
    _name = 'measurement.route'
    _description = 'Measurement Route'

    name = fields.Char('Route Name', required=True)
    line_ids = fields.One2many('measurement.route.line', 'measurement_id', string='Process Lines', copy=True)
    active = fields.Boolean(string="Active", default=True)

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
