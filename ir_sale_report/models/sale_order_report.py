from odoo import models, fields, api
import requests
import json
from datetime import datetime


class SaleOrderReport(models.Model):
    _name = "sale.order.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sale Order Report API"

    voucher_id = fields.Char(string="Voucher Id")
    sl_no = fields.Char(string="S.NO", tracking=True)
    style_no = fields.Char(string="STYLE NO", tracking=True)
    product_id = fields.Many2one("product.product", string="Product", tracking=True)
    product_img1 = fields.Many2one("product.product", string="Product Image", tracking=True)
    product_img2 = fields.Many2one("product.product", string="Product Image", tracking=True)
    buyer_id = fields.Many2one("res.partner", string="Buyer", tracking=True)
    manager_id = fields.Many2one("res.users", string="Manager", tracking=True)
    vno = fields.Char(string="V NO", tracking=True)
    vdate = fields.Date(string="V Date", tracking=True)
    design_no = fields.Char(string="Design NO", tracking=True)
    party = fields.Char(string="Party", tracking=True)
    mc = fields.Char(string="MC", tracking=True)
    product_cat_id = fields.Many2one("product.category", string="MC", tracking=True)
    fit = fields.Char(string="FIT", tracking=True)
    style = fields.Char(string="Style", tracking=True)
    po_description = fields.Char(string="PO Description", tracking=True)
    brand_name = fields.Char(string="Brand Name", tracking=True)
    mrp = fields.Float(string="MRP", tracking=True)
    po_mrp = fields.Float(string="PO MRP", tracking=True)
    color = fields.Char(string="Color", tracking=True)
    po_color = fields.Char(string="PO Color", tracking=True)
    order_qty = fields.Float(string="Order Qty", tracking=True)
    stock_qty = fields.Float(string="Stock Qty", tracking=True)
    production_qty = fields.Float(string="Production Qty", tracking=True)
    po_qty = fields.Float(string="PO Qty", tracking=True)
    article_no = fields.Char(string="Article No", tracking=True)
    po_article = fields.Char(string="PO Article", tracking=True)
    po_no = fields.Char(string="PO NO", tracking=True)
    article_po_status = fields.Char(string="Article PO Status", tracking=True)
    pps_nd_date = fields.Date(string="PPS AND Date", tracking=True)
    pps_expire_date = fields.Date(string="PPS Expire Date", tracking=True)
    stamp_lot_sample = fields.Char(string="STAMP/ LOT SAMPLE", tracking=True)
    lab_test_no = fields.Char(string="Lab Test NO", tracking=True)
    lab_expire_date = fields.Date(string="Lab Expire Date", tracking=True)
    pps_lot_lab_status = fields.Char(string="PPS/LOT/LAB STATUS", tracking=True)
    lab_company = fields.Char(string="Lab Company", tracking=True)
    lab_article_no = fields.Char(string="Lab Article NO", tracking=True)
    lab_content_n_weight = fields.Char(string="Lab Content And Weight", tracking=True)
    po_content_n_weight = fields.Char(string="PO Content And Weight", tracking=True)
    content_weight_status = fields.Char(string="Content Weight Status", tracking=True)
    mrp_rate = fields.Float(string="MRP", tracking=True)
    rate = fields.Float(string="Rate", tracking=True)
    sale_rate = fields.Float(string="Sale Rate", tracking=True)
    po_rate = fields.Float(string="PO Rate", tracking=True)
    season = fields.Char(string="Season", tracking=True)
    po_season = fields.Char(string="PO Season", tracking=True)
    vendor_code = fields.Char(string="Vendor Code", tracking=True)
    contractor_name = fields.Char(string="Contractor Name", tracking=True)
    status = fields.Char(string="Status", tracking=True)
    remark = fields.Char(string="Remark", tracking=True)
    delivery_date = fields.Date(string="Delivery Date", tracking=True)
    size = fields.Char(string="Size", tracking=True)
    ratio = fields.Char(string="Ratio", tracking=True)
    washer = fields.Char(string="Washer", tracking=True)
    washing = fields.Char(string="Washing", tracking=True)
    trims_1 = fields.Char(string="Trims-1", tracking=True)
    trims_2 = fields.Char(string="Trims-2", tracking=True)
    trims_3 = fields.Char(string="Trims-3", tracking=True)
    col_1 = fields.Char(string="Col-1", tracking=True)
    col_2 = fields.Char(string="Col-2", tracking=True)
    col_3 = fields.Char(string="Col-3", tracking=True)
    col_4 = fields.Char(string="Col-4", tracking=True)
    col_5 = fields.Char(string="Col-5", tracking=True)
    col_6 = fields.Char(string="Col-6", tracking=True)
    col_7 = fields.Char(string="Col-7", tracking=True)
    col_8 = fields.Char(string="Col-8", tracking=True)
    col_9 = fields.Date(string="Col-9", tracking=True)
    col_10 = fields.Date(string="Col-10", tracking=True)
    col_11 = fields.Date(string="Col-11", tracking=True)
    col_12 = fields.Date(string="Col-12", tracking=True)
    domain_partner_ids = fields.Many2many("res.partner", compute="_compute_domain_partner_ids")
    domain_product_cat_ids = fields.Many2many("product.category", compute="_compute_domain_partner_ids")

    def _compute_domain_partner_ids(self):
        report_id = self.env['api.report.configration'].search([('user_id', '=', self.env.user.id)], limit=1)
        for res in self:
            res.domain_partner_ids = report_id.partner_ids.ids
            res.domain_product_cat_ids = report_id.product_cat_ids.ids


    def action_open_form_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Sale Order Reports",
            "res_model": "sale.order.report",
            "res_id": self.id,
            "domain": [("id", "=", self.id)],
            "view_mode": "form",
            "context": {'create': False, 'edit': False},
        }

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search([('report_type', '=', 'sale_fabric'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
            if field.is_readonly:
                test_list.append(True)
            else:
                test_list.append(False)
            if field.is_invisible:
                test_list.append(True)
            else:
                test_list.append(False)
        test_list = tuple(test_list)
        key = key + (
            test_list,
        )
        return key

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "list":
            report_id = self.env['api.report.configration'].search([('report_type', '=', 'sale_fabric'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
        return arch, view

    def _cron_fetch_report(self):
        configration = self.env['sale.order.report.configration'].search([('active', '=', True)], limit=1)
        if configration:
            # url = "http://163.53.86.110:9700/ABReportService.svc/GetReportData"
            url = configration.server_url
            headers = {
                'username': configration.user_name,
                'apikey': configration.api_key,
                'company_id': configration.company_id,
                'enterprise_id': configration.enterprise_id,
                'user_id': configration.user_id,
                'Content-Type': 'application/json'
            }
            payload = {
                "report_type": configration.report_type,
                "filter_data": {
                    "period_from": {
                        "value": configration.period_from
                    },
                    "period_to": {
                        "value": configration.period_to
                    },
                    "location": {
                        "value": configration.location
                    }
                }
            }
            response = requests.post(url, json=payload, headers=headers)
            json_response = response.json()
            parsed_data = json.loads(json_response['JsonDataTable'])
            test_json = [parsed_data[0]]
            error_report = []
            items_list = []
            for data in parsed_data:
                items_list.append(data.get('item_id'))
                val = {
                    'voucher_id': data.get('voucher_id'),
                    'vno': data.get('Vno'),
                    'vdate': data.get('vdate'),
                    'design_no': data.get('item_code'),
                    'party': data.get('Party'),
                    'fit': data.get('item_category_name'),
                    'style': data.get('item_master_attribute4_name'),
                    'brand_name': data.get('brand_name'),
                    'mrp': data.get('item_master_mrp'),
                    'color': data.get('item_master_attribute1_name'),
                    'order_qty': data.get('Qty'),
                    'stock_qty': data.get('stock_qty'),
                    'article_no': data.get('item_master_barcode'),
                    'po_no': data.get('item_master_udf4'),
                    'stamp_lot_sample': data.get('item_master_udf3'),
                    'lab_test_no': data.get('item_master_udf1'),
                    'lab_company': data.get('item_master_udf5'),
                    'rate': data.get('rate'),
                    'sale_rate': data.get('sales_rate'),
                    'season': data.get('rack_box'),
                    'size': data.get('item_master_attribute2_name'),
                    'ratio': data.get('item_master_attribute3_name'),
                    'washer': data.get('salt'),
                    'washing': data.get('weigh_scale_barcode'),
                }
                if data.get('group_name'):
                    cat_id = self.env['product.category'].search([('name', '=', data.get('group_name'))])
                    if cat_id:
                        val['product_cat_id'] = cat_id.id

                if data.get('item_master_udf2'):
                    val['pps_nd_date'] = self.parse_date_safe(data.get('item_master_udf2'))
                if data.get('item_id'):
                    product_id = self.env['product.product'].search([('voucher_id', '=', data.get('item_id'))], limit=1)
                    if product_id:
                        val['product_id'] = product_id.id
                        val['product_cat_id'] = product_id.categ_id.id
                    if not product_id.categ_id and data.get('group_name'):
                        cat_id = self.env['product.category'].search([('name', '=', data.get('group_name'))])
                        if cat_id:
                            val['product_cat_id'] = cat_id.id
                try:
                    exist_id = self.env['sale.order.report'].search([('voucher_id', '=', data.get('voucher_id'))], limit=1)
                    print("exist_id==", exist_id)
                    if exist_id:
                        exist_id.write(val)
                    else:
                        report_ids = self.env['sale.order.report'].create(val)
                        print("report_ids==", report_ids)
                except Exception as e:
                    error_report.append(data.get('name'))
                    print("===", e)
            print("items_list==", items_list)

    def parse_date_safe(self, date_str):
        try:
            # Use correct format according to your data
            return datetime.strptime(date_str, "%d/%m/%Y").date() if date_str else False
        except Exception:
            return False


class SaleOrderReportConfigration(models.Model):
    _name = "sale.order.report.configration"

    server_url = fields.Char(string="Server Url")
    user_name = fields.Char(string="Username")
    api_key = fields.Char(string="Api Key")
    company_id = fields.Char(string="Company Id")
    enterprise_id = fields.Char(string="Enterprise Id")
    user_id = fields.Char(string="User Id")
    report_type = fields.Integer("Report Type")
    period_from = fields.Char(string="Period From", help="YYYY-MM-DD 00:00:00")
    period_to = fields.Char(string="Period To", help="YYYY-MM-DD 00:00:00")
    active = fields.Boolean(string="Active", default=True)
    location = fields.Char(string="Location")
