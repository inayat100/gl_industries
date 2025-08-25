from odoo import models, fields, api



class MeasurementProcess(models.Model):
    _name = 'pps.process'
    _description = 'PPS Process'
    _order = 'id'

    name = fields.Char('Process Name', required=True)
    description = fields.Text('Description')



class MeasurementRoute(models.Model):
    _name = 'pps.route'
    _description = 'PPS Route'

    name = fields.Char('Route Name', required=True)
    line_ids = fields.One2many('pps.route.line', 'pps_id', string='Process Lines', copy=True)


class MeasurementRouteLine(models.Model):
    _name = 'pps.route.line'
    _description = 'PPS Route Line'
    _order = 'sequence, id'

    pps_id = fields.Many2one('pps.route', string='PPS Route', required=True, ondelete='cascade')
    process_id = fields.Many2one('pps.process', string='Process', required=True)
    sequence = fields.Integer('Sequence', required=True, default=10)
    col1 = fields.Char(string="Col-1")
    col2 = fields.Char(string="Col-2")
    col3 = fields.Char(string="Col-3")
    col4 = fields.Char(string="Col-4")
    remark = fields.Char(string="Remark")