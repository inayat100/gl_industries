from odoo import models, fields, api



class ApiReportConfigration(models.Model):
    _inherit = "api.report.configration"

    color_ids = fields.Many2many("color.master", string="Color")
    product_design_type_ids = fields.Many2many("product.design.type", string="Product Type")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.report_type == 'mrp.bom':
            res.user_id.bom_report_id = res.id
            group_xml_id = "ir_bom.group_bom_route_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'mrp.bom.line':
            res.user_id.bom_line_report_id = res.id
            group_xml_id = "ir_bom.group_bom_line_route_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        return res

    def write(self, vals):
        self.user_id.bom_report_id = False
        self.user_id.bom_line_report_id = False
        report_obj = self.env['api.report.configration']
        res = super(ApiReportConfigration, self).write(vals)
        report_ids = report_obj.search([('user_id', '=', self.user_id.id)])
        for report in report_ids:
            if report.report_type == 'mrp.bom':
                report.user_id.bom_report_id = report.id
                group_xml_id = "ir_bom.group_bom_route_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'mrp.bom.line':
                report.user_id.bom_line_report_id = report.id
                group_xml_id = "ir_bom.group_bom_line_route_access_right"
                report.user_id.refresh_user_group(group_xml_id)
        return res