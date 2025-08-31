# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class QualityProcess(models.Model):
    _name = 'quality.process'
    _description = 'Quality Work Process'
    _order = 'id'

    name = fields.Char('Process Name', required=True)
    description = fields.Text('Description')



class QualityRoute(models.Model):
    _name = 'quality.route'
    _description = 'Job Work Route'

    name = fields.Char('Route Name', required=True)
    line_ids = fields.One2many('quality.route.line', 'route_id', string='Process Lines', copy=True)
    active = fields.Boolean(string="Active", default=True)

class QualityRouteLine(models.Model):
    _name = 'quality.route.line'
    _description = 'Quality Route Line'
    _order = 'sequence, id'

    route_id = fields.Many2one('quality.route', string='Quality Route', required=True, ondelete='cascade')
    process_id = fields.Many2one('quality.process', string='Process', required=True)
    remark = fields.Char(string="Remark")
    sequence = fields.Integer('Sequence', required=True, default=10)
