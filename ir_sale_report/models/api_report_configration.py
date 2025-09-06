from odoo import models, fields, api
from odoo.exceptions import UserError

report_type_list = [
    ('sale_order', 'Sale Order Report'),
    ('sample_planning', 'Sample Planning'),
    ('production_planning', 'Production Planning'),
    ('sale_fabric', 'Sales Fabric'),
    ('product_product', 'Product Master'),
    ('component_report', 'Component Report'),
    ('job_order_report', 'Job Order Report'),
    ('so', 'Sale Orders'),
    ('mo', 'Manufacturing Orders'),
    ('po', 'Purchase Orders'),
    ('measurement.report', 'Measurement Report'),
    ('pps.lab', 'PPS Lab Report'),
    ('quality.report', 'Quality Report'),
]

class ApiReportConfigration(models.Model):
    _name = "api.report.configration"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    report_id = fields.Many2one("ir.model", string="Report Model")
    user_id = fields.Many2one("res.users", string="User", copy=False)
    report_type = fields.Selection(report_type_list, string="Report Type", required=True)
    disable_edit = fields.Boolean(string="Disable Edit")
    disable_delete = fields.Boolean(string="Disable Delete")
    disable_create = fields.Boolean(string="Disable Create")
    line_ids = fields.One2many("api.report.configration.line", "report_id", string="Lines")

    customer_ids = fields.Many2many(
        "res.partner",
        "order_customers_rel",
        "order_id", "partner_id",
        string="Customers"
    )
    vendor_ids = fields.Many2many(
        "res.partner",
        "order_vendors_rel",
        "order_id", "vendor_id",
        string="Vendors"
    )
    user_ids = fields.Many2many("res.users", string="Users")
    product_cat_ids = fields.Many2many("product.category", string="MC")
    brand_ids = fields.Many2many(
        "brand.master",
        "order_brands_rel",
        "order_id", "brand_id",
        string="Brands"
    )
    active = fields.Boolean(string="Active", default=True)



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
        elif self.report_type == 'so':
            report_id = self.env.ref("sale.model_sale_order")
            self.report_id = report_id.id
        elif self.report_type == 'mo':
            report_id = self.env.ref("mrp.model_mrp_production")
            self.report_id = report_id.id
        elif self.report_type == 'po':
            report_id = self.env.ref("purchase.model_purchase_order")
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

    @api.model_create_multi
    def create(self, vals_list):
        report_obj = self.env['api.report.configration']
        for val in vals_list:
            report_type = val.get('report_type')
            user_id = val.get('user_id')
            user = self.env['res.users'].browse(user_id)
            report_id = report_obj.search([('report_type', '=', report_type), ('user_id', '=', user_id)])
            if report_id and len(report_id) > 1:
                raise UserError(f"{report_id.name} This Report Type Is Already Exist For Same User. {user.name}")
        res = super().create(vals_list)
        if res.report_type == 'sale_order':
            res.user_id.sale_order_report_id = res.id
            group_xml_id = "ir_sale_report.group_sale_order_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'sample_planning':
            res.user_id.sample_planning_report_id = res.id
            group_xml_id = "ir_sale_report.group_sample_planing_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'sale_fabric':
            res.user_id.fabric_yardage_report_id = res.id
            group_xml_id = "ir_sale_report.group_sales_order_fabric_yardage_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'production_planning':
            res.user_id.production_planing_report_id = res.id
            group_xml_id = "ir_sale_report.group_production_planing_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        elif res.report_type == 'component_report':
            res.user_id.component_report_report_id = res.id
            group_xml_id = "ir_sale_report.group_component_report_access_right"
            res.user_id.refresh_user_group(group_xml_id)
        return res

    def write(self, vals):
        self.user_id.sale_order_report_id = False
        self.user_id.sample_planning_report_id = False
        self.user_id.fabric_yardage_report_id = False
        self.user_id.production_planing_report_id = False
        report_obj = self.env['api.report.configration']
        res = super(ApiReportConfigration, self).write(vals)

        report_id = report_obj.search([('report_type', '=', self.report_type), ('user_id', '=', self.user_id.id)])
        if report_id and len(report_id) > 1:
            raise UserError(f"{report_id.name} This Report Type Is Already Exist For Same User..{self.user_id.name}")
        report_ids = report_obj.search([('user_id', '=', self.user_id.id)])
        for report in report_ids:
            if report.report_type == 'sale_order':
                report.user_id.sale_order_report_id = report.id
                group_xml_id = "ir_sale_report.group_sale_order_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'sample_planning':
                report.user_id.sample_planning_report_id = report.id
                group_xml_id = "ir_sale_report.group_sample_planing_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'sale_fabric':
                report.user_id.fabric_yardage_report_id = report.id
                group_xml_id = "ir_sale_report.group_sales_order_fabric_yardage_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'production_planning':
                report.user_id.production_planing_report_id = report.id
                group_xml_id = "ir_sale_report.group_production_planing_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
            elif report.report_type == 'component_report':
                report.user_id.component_report_report_id = report.id
                group_xml_id = "ir_sale_report.group_component_report_access_right"
                report.user_id.refresh_user_group(group_xml_id)
        return res



class ApiReportConfigrationLine(models.Model):
    _name = "api.report.configration.line"

    report_id = fields.Many2one("api.report.configration", string="Report")
    field_id = fields.Many2one("ir.model.fields", string="Fields")
    is_readonly = fields.Boolean(string="Readonly")
    is_invisible = fields.Boolean(string="Invisible")
    is_edit = fields.Boolean(string="Write")