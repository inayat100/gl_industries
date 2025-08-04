from odoo import models, fields, api
import requests
import json
from datetime import datetime, date, timedelta


class SaleOrderReport(models.Model):
    _name = "sale.order.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sale Order Report API"


    is_favorite = fields.Boolean(string="Favorite")
    voucher_id = fields.Char(string="Voucher Id")
    sl_no = fields.Char(string="Proto Sample", tracking=True)
    style_no = fields.Char(string="PO PDF", tracking=True)
    product_id = fields.Many2one("product.product", string="Product", tracking=True)
    pd_img1 = fields.Binary(string="Product Image")
    pd_img2 = fields.Binary(string="Back Image")
    buyer_id = fields.Many2one("res.partner", string="Buyer", tracking=True)
    buyer_email = fields.Char(string="Buyer Email")
    doc_url = fields.Char(string="Doc Url")
    partner_manager_id = fields.Many2one("res.partner", string="Manager", tracking=True)
    vno = fields.Char(string="V NO", tracking=True)
    vdate = fields.Date(string="V Date", tracking=True)
    design_no = fields.Char(string="Design NO", tracking=True)
    party_id = fields.Many2one("res.partner", string="Party", tracking=True)
    product_cat_id = fields.Many2one("product.category", string="MC", tracking=True)
    garment_average = fields.Char(string="Garment Averages")
    febric_product_id = fields.Many2one("product.product", string="FEBRIC SORT NO")
    fit = fields.Char(string="FIT", tracking=True)
    style = fields.Char(string="Style", tracking=True)
    po_description = fields.Char(string="PO Description", tracking=True)
    brand_id = fields.Many2one("brand.master", string="Brand Name", tracking=True)
    mrp = fields.Float(string="MRP", tracking=True)
    po_mrp = fields.Float(string="PO MRP", tracking=True)
    color = fields.Char(string="Color", tracking=True)
    color_id = fields.Many2one("color.master", string="Color", tracking=True)
    po_color_id = fields.Many2one("color.master", string="PO Color", tracking=True)
    order_qty = fields.Float(string="Order Qty", tracking=True)
    stock_qty = fields.Float(string="Stock Qty", tracking=True)
    production_qty = fields.Float(string="Production Qty", tracking=True)
    po_qty = fields.Float(string="PO Qty", tracking=True)
    po_qty_approval = fields.Char(string="PO QTY APPROVAL")
    article_no = fields.Char(string="Article No", tracking=True)
    po_article = fields.Char(string="PO Article", tracking=True)
    system_po_no = fields.Char(string="System PO NO")
    po_no = fields.Char(string="PO NO", tracking=True)
    article_po_status = fields.Char(string="Article PO Status", tracking=True)
    pps_nd_date = fields.Char(string="PPS No", tracking=True)
    pps_expire_date = fields.Date(string="PPS Expire Date", tracking=True)
    stamp_lot_sample = fields.Char(string="STAMP/ LOT SAMPLE", tracking=True)
    lab_test_no = fields.Char(string="Lab Test NO", tracking=True)
    lab_expire_date = fields.Date(string="Lab Expire Date", tracking=True)
    pps_lot_lab_status = fields.Char(string="PPS/LOT/LAB STATUS", tracking=True)
    lab_company = fields.Char(string="Lab Content", tracking=True)
    tafta_content = fields.Char(string="TAFTA CONTENT")
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
    vendor_id = fields.Many2one("res.partner", string="Contractor Name",  tracking=True)
    status = fields.Char(string="Status", tracking=True)
    remark = fields.Char(string="Remark", tracking=True)
    delivery_date = fields.Date(string="Delivery Date", tracking=True)
    qc_report_no = fields.Char(string="QC Report NO")
    qc_report_date = fields.Date(string="QC Report Date")
    size = fields.Char(string="Size", tracking=True)
    ratio = fields.Char(string="Ratio", tracking=True)
    washer = fields.Char(string="Washer", tracking=True)
    washing = fields.Char(string="Washing", tracking=True)
    trims_1 = fields.Date(string="GOODS SENDING DATE", tracking=True)
    trims_2 = fields.Date(string="TAFTA MANUFACTURING MONTH", tracking=True)
    trims_3 = fields.Char(string="Final Comment", tracking=True)
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
    company_id = fields.Many2one("res.company", string="Company")
    active = fields.Boolean(string="Active", default=True)
    date_red = fields.Boolean(string="Date Red", compute="_compute_date_red")
    lab_date_red = fields.Boolean(string="Lab Date Red", compute="_compute_date_red")
    delivery_date_date_red = fields.Boolean(string="Delivery Date Red", compute="_compute_date_red")
    qc_report_date_date_red = fields.Boolean(string="Delivery Date Red", compute="_compute_date_red")

    def _compute_date_red(self):
        for res in self:
            if res.pps_expire_date:
                if res.pps_expire_date <= date.today() + timedelta(days=15):
                    res.date_red = True
                else:
                    res.date_red = False
            else:
                res.date_red = False

            if res.lab_expire_date:
                if res.lab_expire_date <= date.today() + timedelta(days=15):
                    res.lab_date_red = True
                else:
                    res.lab_date_red = False
            else:
                res.lab_date_red = False

            if res.delivery_date:
                if res.delivery_date <= date.today() + timedelta(days=1):
                    res.delivery_date_date_red = True
                else:
                    res.delivery_date_date_red = False
            else:
                res.delivery_date_date_red = False

            if res.qc_report_date:
                if res.qc_report_date <= date.today() - timedelta(days=25):
                    res.qc_report_date_date_red = True
                else:
                    res.qc_report_date_date_red = False
            else:
                res.qc_report_date_date_red = False


    @api.onchange('buyer_id')
    def _onchange_field_data(self):
        self.buyer_email = self.buyer_id.email
        # print("self.product_id.image_1920", self.product_id.image_1920)
        # self.pd_img1 = self.product_id.image_1920

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.pd_img1 = self.product_id.image_1920
        else:
            self.pd_img1 = False

    def _compute_domain_partner_ids(self):
        report_id = self.env['api.report.configration'].search([('user_id', '=', self.env.user.id)], limit=1)
        for res in self:
            res.domain_partner_ids = []
            res.domain_product_cat_ids = []

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
        report_id = self.env['api.report.configration'].search([('report_type', '=', 'sale_order'), ('user_id', '=', self.env.user.id)], limit=1)
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
        if report_id.disable_create:
            test_list.append(True)
        else:
            test_list.append(False)
        if report_id.disable_delete:
            test_list.append(True)
        else:
            test_list.append(False)
        if report_id.disable_edit:
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
        if view_type in ["list", "form"]:
            report_id = self.env['api.report.configration'].search([('report_type', '=', 'sale_order'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
            if report_id.disable_create:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("create", "0")
            if report_id.disable_delete:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("delete", "0")
            if report_id.disable_edit:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("edit", "0")
        return arch, view

    def _cron_fetch_report(self):
        configration_ids = self.env['sale.order.report.configration'].search([('active', '=', True)])
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for configration in configration_ids:
            if configration:
                # url = "http://163.53.86.110:9700/ABReportService.svc/GetReportData"
                url = configration.server_url
                headers = {
                    'username': configration.user_name,
                    'apikey': configration.api_key,
                    'company_id': configration.company_key,
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
                            "value": configration.period_to or today
                        },
                        "location": {
                            "value": configration.location
                        }
                    }
                }
                print("payload=-=-", payload)
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
                        'fit': data.get('item_category_name'),
                        'style': data.get('item_master_attribute4_name'),
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
                    if configration.company_id:
                        val['company_id'] = configration.company_id.id
                    if data.get('group_name'):
                        cat_id = self.env['product.category'].search([('name', '=', data.get('group_name'))])
                        if cat_id:
                            val['product_cat_id'] = cat_id.id
                    if data.get('item_master_udf2'):
                        val['pps_nd_date'] = data.get('item_master_udf2')
                    if data.get('item_id'):
                        product_id = self.env['product.product'].search([('voucher_id', '=', data.get('item_id'))], limit=1)
                        if product_id:
                            val['product_id'] = product_id.id
                            val['product_cat_id'] = product_id.categ_id.id
                            val['pd_img1'] = product_id.image_1920
                            val['pd_img2'] = product_id.product_img_1
                        if not product_id.categ_id and data.get('group_name'):
                            cat_id = self.env['product.category'].search([('name', '=', data.get('group_name'))])
                            if cat_id:
                                val['product_cat_id'] = cat_id.id
                    if data.get('Party'):
                        partner_id = self.env['res.partner'].search([('name', '=', data.get('Party'))], limit=1)
                        if partner_id:
                            val['party_id'] = partner_id.id
                        else:
                            partner_id = self.env['res.partner'].create([{
                                'name': data.get('Party')
                            }])
                    if data.get('brand_name'):
                        brand_id = self.env['brand.master'].search([('name', '=', data.get('brand_name'))], limit=1)
                        if brand_id:
                            val['brand_id'] = brand_id.id
                        else:
                            brand_id = self.env['brand.master'].create([{
                                'name': data.get('brand_name')
                            }])
                            val['brand_id'] = brand_id.id
                    if data.get('item_master_attribute1_name'):
                        color_id = self.env['color.master'].search([('name', '=', data.get('item_master_attribute1_name'))], limit=1)
                        if color_id:
                            val['color_id'] = color_id.id
                        else:
                            color_id = self.env[''].create([{
                                'name': data.get('item_master_attribute1_name')
                            }])
                            val['color_id'] = color_id.id
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
    company_id = fields.Many2one("res.company", string="Company")
    company_key = fields.Char(string="Company Id")
    enterprise_id = fields.Char(string="Enterprise Id")
    user_id = fields.Char(string="User Id")
    report_type = fields.Integer("Report Type")
    period_from = fields.Char(string="Period From", help="YYYY-MM-DD 00:00:00")
    period_to = fields.Char(string="Period To", help="YYYY-MM-DD 00:00:00")
    active = fields.Boolean(string="Active", default=True)
    location = fields.Char(string="Location")
