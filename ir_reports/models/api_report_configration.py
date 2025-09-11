from odoo import models, fields, api
from odoo.exceptions import UserError

document_type_list = [
    ('po_article', 'PO/ARTICLE'),
    ('pps', 'PPS'),
    ('lab_test', 'Lab Test'),
    ('photo_sample', 'Photo Sample'),
    ('fit_sample', 'FIT Sample'),
]

class ApiReportConfigration(models.Model):
    _inherit = "api.report.configration"

    stage_ids = fields.Many2many("stage.master", string="Stage")
    document_type = fields.Selection(document_type_list, string="Document type")
    document_type_ids = fields.Many2many("document.type.master", string="Document type")

    @api.onchange('report_type')
    def _onchange_report_type_model(self):
        print("self.report_type", self.report_type)
        if self.report_type == 'measurement.report':
            report_ids = [self.env.ref("ir_reports.model_measurement_report").id, self.env.ref("ir_reports.model_measurement_report_line").id]
            self.report_ids = [(6, 0, report_ids)]
            report_id = self.env.ref("ir_reports.model_measurement_report")
            self.report_id = report_id.id
        elif self.report_type == 'pps.lab':
            report_ids = [self.env.ref("ir_reports.model_pps_lab").id,
                          self.env.ref("ir_reports.model_pps_lab_line").id]
            self.report_ids = [(6, 0, report_ids)]
            report_id = self.env.ref("ir_reports.model_pps_lab")
            self.report_id = report_id.id
        elif self.report_type == 'quality.report':
            report_ids = [self.env.ref("ir_reports.model_quality_report").id,
                          self.env.ref("ir_reports.model_quality_report_trims").id,
                          self.env.ref("ir_reports.model_quality_report_feed_off_machine").id,
                          self.env.ref("ir_reports.model_quality_report_sewing_machine").id,
                          self.env.ref("ir_reports.model_quality_report_construction").id]
            self.report_ids = [(6, 0, report_ids)]
            report_id = self.env.ref("ir_reports.model_quality_report")
            self.report_id = report_id.id

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.report_type == 'measurement.report':
            res.user_id.measurement_report_id = res.id
            group_xml_id = "ir_reports.group_measurement_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'pps.lab':
            res.user_id.pps_report_id = res.id
            group_xml_id = "ir_reports.group_pps_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'quality.report':
            res.user_id.quality_report_id = res.id
            group_xml_id = "ir_reports.group_quality_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        return res

    def write(self, vals):
        self.user_id.quality_report_id = False
        self.user_id.pps_report_id = False
        self.user_id.measurement_report_id = False
        report_obj = self.env['api.report.configration']
        res = super(ApiReportConfigration, self).write(vals)
        report_ids = report_obj.search([('user_id', '=', self.user_id.id)])
        for report in report_ids:
            if report.report_type == 'measurement.report':
                report.user_id.measurement_report_id = report.id
                group_xml_id = "ir_reports.group_measurement_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'pps.lab':
                report.user_id.pps_report_id = report.id
                group_xml_id = "ir_reports.group_pps_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'quality.report':
                report.user_id.quality_report_id = report.id
                group_xml_id = "ir_reports.group_quality_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
        return res