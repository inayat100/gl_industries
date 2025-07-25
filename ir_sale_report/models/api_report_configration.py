from odoo import models, fields, api

report_type_list = [
    ('sale_order', 'Sale Order Report'),
    ('sample_planning', 'Sample Planning'),
    ('production_planning', 'Production Planning'),
    ('sale_fabric', 'Sales Fabric'),
    ('product_product', 'Product Master'),
    ('component_report', 'Component Report'),
    ('job_order_report', 'Job Order Report')
]

class ApiReportConfigration(models.Model):
    _name = "api.report.configration"

    name = fields.Char(string="Name")
    report_id = fields.Many2one("ir.model", string="Report Model")
    user_id = fields.Many2one("res.users", string="User")
    partner_ids = fields.Many2many("res.partner", string="Partner")
    user_ids = fields.Many2many("res.users", string="Manger")
    product_cat_ids = fields.Many2many("product.category", string="MC")
    report_type = fields.Selection(report_type_list, string="Report Type", required=True)
    line_ids = fields.One2many("api.report.configration.line", "report_id", string="Lines")
    disable_create = fields.Boolean(string="Disable Create")
    disable_edit = fields.Boolean(string="Disable Edit")
    disable_delete = fields.Boolean(string="Disable Delete")

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type == 'sale_order':
            report_id = self.env.ref("ir_sale_report.model_sale_order_report")
            self.report_id = report_id.id
        elif self.report_type == 'sample_planning':
            report_id = self.env.ref("ir_sale_report.model_sample_planing")
            self.report_id = report_id.id
        elif self.report_type == 'production_planning':
            report_id = self.env.ref("ir_sale_report.model_production_planing")
            self.report_id = report_id.id
        elif self.report_type == 'sale_fabric':
            report_id = self.env.ref("ir_sale_report.model_sales_order_fabric")
            self.report_id = report_id.id
        elif self.report_type == 'product_product':
            report_id = self.env.ref("product.model_product_template")
            self.report_id = report_id.id
        elif self.report_type == 'component_report':
            report_id = self.env.ref("ir_sale_report.model_production_move_report")
            self.report_id = report_id.id


    def action_create_line(self):
        field_list = []
        for field in self.report_id.field_id:
            field_list.append((0, 0, {
                'field_id': field.id,
                'is_readonly': False,
                'is_invisible': False,
            }))
        if self.line_ids:
            self.line_ids = [(5, 0, 0)]
        self.line_ids = field_list



class ApiReportConfigrationLine(models.Model):
    _name = "api.report.configration.line"

    report_id = fields.Many2one("api.report.configration", string="Report")
    field_id = fields.Many2one("ir.model.fields", string="Fields")
    is_readonly = fields.Boolean(string="Readonly")
    is_invisible = fields.Boolean(string="Invisible")
    is_edit = fields.Boolean(string="Write")