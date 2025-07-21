# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobWorkProcess(models.Model):
    _name = 'job.work.process'
    _description = 'Job Work Process'
    _order = 'id'

    name = fields.Char('Process Name', required=True)
    description = fields.Text('Description')



class JobWorkRoute(models.Model):
    _name = 'job.work.route'
    _description = 'Job Work Route'

    name = fields.Char('Route Name', required=True)
    line_ids = fields.One2many('job.work.route.line', 'route_id', string='Process Lines', copy=True)


class JobWorkRouteLine(models.Model):
    _name = 'job.work.route.line'
    _description = 'Job Work Route Line'
    _order = 'sequence, id'

    route_id = fields.Many2one('job.work.route', string='Job Work Route', required=True, ondelete='cascade')
    process_id = fields.Many2one('job.work.process', string='Process', required=True)
    sequence = fields.Integer('Sequence', required=True, default=10)
    # Optional default fields
    rate = fields.Float('Default Rate')
    days_to_complete = fields.Integer('Days to Complete', default=1, help="Estimated days this process will take.")
