from odoo import models, fields, api
import requests
import json
from odoo.exceptions import UserError
import base64
import sys
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_api_product = fields.Boolean("Api Product")
    voucher_id = fields.Char(string="Voucher Id")
    fit_measurement_id = fields.Many2one("fit.measurement", string="FIT/Measurement")
    purchase_rate = fields.Float(string="Purchase rate")
    inventory_ledger_name = fields.Char(string="Inventory Ledger Name")
    batch_wise_inventory = fields.Boolean(string="Batch Wise Inventory")
    lab_comp = fields.Char(string="LAB/Comp")
    pps_width = fields.Char(string="PPS/WIDTH")
    stamp_width = fields.Char(string="STAMP/WEIGHT")
    po_number_count = fields.Char(string="PO NUMBER/COUN")
    content_pentone = fields.Char(string="CONTENT/Pentone")
    mrp = fields.Float(string="MRP")
    vendor_name = fields.Char(string="WASHER Name")
    season_id = fields.Many2one("season.master", string="Season")
    color_id = fields.Many2one("color.master", string="Color")
    size_id = fields.Many2one("size.master", string="Size")
    ratio_id = fields.Many2one("ratio.master", string="Ratio")
    design_id = fields.Many2one("design.master", string="Design")
    print_embroidery_id = fields.Many2one("embroidery.master", string="Print Embroidery")
    brand_id = fields.Many2one("brand.master", string="Brand")
    product_design_type_id = fields.Many2one("product.design.type", string="Product Type")
    product_img_1 = fields.Binary(string="Back Image")
    product_img_2 = fields.Binary(string="Image1")
    product_img_3 = fields.Binary(string="Image2")
    design_no = fields.Char(string="Design NO")

    fabric_short_no = fields.Float(string="Fabric short no.")
    fabric_qty = fields.Float(string="Fabric Qty")
    product_qty = fields.Float(string="Product Qty")
    pocket_no = fields.Float(string="Pocket No")
    buttons = fields.Float(string="Buttons")
    lastic = fields.Char(string="Lastic")
    patch = fields.Char(string="Patch")
    fabric_weight = fields.Char(string="Fabric Weight")
    fabric_contruction = fields.Char(string="Fabric Contruction")
    col_1 = fields.Char(string="Col1")
    col_2 = fields.Char(string="Col2")
    col_3 = fields.Char(string="Col3")
    col_4 = fields.Char(string="Col4")
    col_5 = fields.Char(string="Col5")
    col_6 = fields.Char(string="Col6")
    api_default_code = fields.Char(string="Default Code")
    api_barcode = fields.Char(string="Barcode")

    febric_product_id = fields.Many2one("product.product", string="Febric short no.")
    decp = fields.Char(string="DECP")
    vendor_code = fields.Char(string="Vendor Code")
    washing_item_id = fields.Many2one("washing.item", string="WASHING")

    @api.constrains('name')
    def _check_unique_name(self):
        for rec in self:
            if rec.name:
                exists = self.search([
                    ('name', '=', rec.name),
                    ('id', '!=', rec.id)
                ], limit=1)
                if exists:
                    raise UserError("Product name must be unique!")

    @api.constrains('product_img_1', 'product_img_2', 'product_img_3')
    def _check_image_size(self):
        max_size_kb = 100  # Limit in KB
        max_size_bytes = max_size_kb * 1024
        for rec in self:
            if rec.product_img_1:
                image_size_bytes = sys.getsizeof(base64.b64decode(rec.product_img_1))
                if image_size_bytes > max_size_bytes:
                    raise UserError(f"Image size exceeds {max_size_kb} KB limit.")
            if rec.product_img_2:
                image_size_bytes = sys.getsizeof(base64.b64decode(rec.product_img_2))
                if image_size_bytes > max_size_bytes:
                    raise UserError(f"Image size exceeds {max_size_kb} KB limit.")
            if rec.product_img_3:
                image_size_bytes = sys.getsizeof(base64.b64decode(rec.product_img_3))
                if image_size_bytes > max_size_bytes:
                    raise UserError(f"Image size exceeds {max_size_kb} KB limit.")
            if rec.image_1920:
                image_size_bytes = sys.getsizeof(base64.b64decode(rec.image_1920))
                if image_size_bytes > max_size_bytes:
                    raise UserError(f"Image size exceeds {max_size_kb} KB limit.")

    def _cron_create_product(self):
        configration_ids = self.env['product.template.configration'].search([('active', '=', True)])
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
                response = requests.post(url, json=payload, headers=headers)
                json_response = response.json()
                parsed_data = json.loads(json_response['JsonDataTable'])
                test_list = [parsed_data[0]]
                error_product = []
                for data in parsed_data:
                    val = {
                        'is_api_product': True,
                        'voucher_id': data.get('voucher_id') or '',
                        'name': data.get('name') or '',
                        'api_default_code': data.get('code') or '',
                        'active': data.get('Inactive') or '',
                        'l10n_in_hsn_code': data.get('gst_classification_name') or '',
                        'list_price': data.get('sales_rate') or 0.0,
                        'description_purchase': data.get('purchase_description') or '',
                        'purchase_rate': data.get('purchase_rate') or 0.0,
                        'inventory_ledger_name': data.get('inventory_ledger_name') or '',
                        'batch_wise_inventory': data.get('batch_wise_inventory') or False,
                        'lab_comp': data.get('udf1') or '',
                        'pps_width': data.get('udf2') or '',
                        'stamp_width': data.get('udf3') or '',
                        'po_number_count': data.get('udf4') or '',
                        'content_pentone': data.get('udf5') or '',
                        'api_barcode': data.get('barcode') or '',
                        'mrp': data.get('mrp') or 0.0,
                        # 'default_code': data.get('tax_rate') or '',
                        # 'default_code': data.get('mapping_code') or '',
                        'vendor_name': data.get('salt') or '',
                    }
                    if configration.company_id:
                        val['company_id'] = configration.company_id.id
                    if data.get('type') and data.get('type') == 'Service':
                        val['type'] = 'service'
                    else:
                        val['type'] = 'consu'
                        val['is_storable'] = True
                        if data.get('batch_wise_inventory'):
                            val['tracking'] = 'lot'
                    if data.get('group_name'):
                        category_id = self.env['product.category'].search([('name', '=', data.get('group_name'))], limit=1)
                        if category_id:
                            val['categ_id'] = category_id.id
                        else:
                            category_id = self.env['product.category'].create([{'name': data.get('group_name')}])
                            val['categ_id'] = category_id.id
                    if data.get('stock_unit_name'):
                        uom_id = self.env['uom.uom'].search([('name', '=', data.get('stock_unit_name'))], limit=1)
                        if uom_id:
                            val['uom_id'] = uom_id.id
                        else:
                            uom_cat_id = self.env.ref("uom.product_uom_categ_unit")
                            uom_id = self.env['uom.uom'].create([{'category_id':uom_cat_id.id, 'name': data.get('stock_unit_name'), 'uom_type':'bigger'}])
                            val['uom_id'] = uom_id.id
                    if data.get('rack_box'):
                        season_id = self.env['season.master'].search([('name', '=', data.get('rack_box'))], limit=1)
                        if season_id:
                            val['season_id'] = season_id.id
                        else:
                            season_id = self.env['season.master'].create([{'name': data.get('rack_box')}])
                            val['season_id'] = season_id.id
                    if data.get('attribute1_name'):
                        color_id = self.env['color.master'].search([('name', '=', data.get('attribute1_name'))], limit=1)
                        if color_id:
                            val['color_id'] = color_id.id
                        else:
                            color_id = self.env['color.master'].create([{'name': data.get('attribute1_name')}])
                            val['color_id'] = color_id.id
                    if data.get('attribute2_name'):
                        size_id = self.env['size.master'].search([('name', '=', data.get('attribute2_name'))], limit=1)
                        if size_id:
                            val['size_id'] = size_id.id
                        else:
                            size_id = self.env['size.master'].create([{'name': data.get('attribute2_name')}])
                            val['size_id'] = size_id.id
                    if data.get('attribute3_name'):
                        ratio_id = self.env['ratio.master'].search([('name', '=', data.get('attribute3_name'))], limit=1)
                        if ratio_id:
                            val['ratio_id'] = ratio_id.id
                        else:
                            ratio_id = self.env['ratio.master'].create([{'name': data.get('attribute3_name')}])
                            val['ratio_id'] = ratio_id.id
                    if data.get('attribute4_name'):
                        design_id = self.env['design.master'].search([('name', '=', data.get('attribute4_name'))], limit=1)
                        if design_id:
                            val['design_id'] = design_id.id
                        else:
                            design_id = self.env['design.master'].create([{'name': data.get('attribute4_name')}])
                            val['design_id'] = design_id.id
                    if data.get('attribute5_name'):
                        print_embroidery_id = self.env['embroidery.master'].search([('name', '=', data.get('attribute5_name'))], limit=1)
                        if print_embroidery_id:
                            val['print_embroidery_id'] = print_embroidery_id.id
                        else:
                            print_embroidery_id = self.env['embroidery.master'].create([{'name': data.get('attribute5_name')}])
                            val['print_embroidery_id'] = print_embroidery_id.id
                    if data.get('brand_name'):
                        brand_id = self.env['brand.master'].search([('name', '=', data.get('brand_name'))], limit=1)
                        if brand_id:
                            val['brand_id'] = brand_id.id
                        else:
                            brand_id = self.env['brand.master'].create([{'name': data.get('brand_name')}])
                            val['brand_id'] = brand_id.id
                    if data.get('category_name'):
                        fit_measurement_id = self.env['fit.measurement'].search([('name', '=', data.get('category_name'))], limit=1)
                        if fit_measurement_id:
                            val['fit_measurement_id'] = fit_measurement_id.id
                        else:
                            fit_measurement_id = self.env['fit.measurement'].create([{'name': data.get('category_name')}])
                            val['fit_measurement_id'] = fit_measurement_id.id
                    if data.get('type'):
                        product_design_type_id = self.env['product.design.type'].search([('name', '=', data.get('type'))], limit=1)
                        if product_design_type_id:
                            val['product_design_type_id'] = product_design_type_id.id
                        else:
                            product_design_type_id = self.env['product.design.type'].create([{'name': data.get('type')}])
                            val['product_design_type_id'] = product_design_type_id.id
                    if data.get('type') and data.get('type') == 'FinishProduct':
                        mto_id = self.env.ref("stock.route_warehouse0_mto")
                        mrp_id = self.env.ref("mrp.route_warehouse0_manufacture")
                        val['route_ids'] = [mrp_id.id, mto_id.id]
                    else:
                        buy_id = self.env.ref("purchase_stock.route_warehouse0_buy")
                        val['route_ids'] = [buy_id.id]
                    try:
                        exist_product_id = self.env['product.template'].search([('voucher_id', '=', data.get('voucher_id'))], limit=1)
                        if exist_product_id.id == 128:
                            print("@@@@@@@@@@@@@@@@@@@@@@", val)
                        if exist_product_id:
                            exist_product_id.write(val)
                        else:
                            product_ids = self.env['product.template'].create([val])
                    except Exception as e:
                        error_product.append(data.get('name'))
                        print("data===", val)
                        print("===", e)
                # print("Errors product", len(error_product))
                # print("Error Product List", error_product)

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'product_product'), ('user_id', '=', self.env.user.id)], limit=1)
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
        if view_type == "form":
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'product_product'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("invisible", "1")
            if report_id.disable_create:
                for node in arch.xpath("//form"):
                    node.set("create", "0")
            if report_id.disable_delete:
                for node in arch.xpath("//form"):
                    node.set("delete", "0")
            if report_id.disable_edit:
                for node in arch.xpath("//form"):
                    node.set("edit", "0")
        return arch, view


class SaleOrderReportConfigration(models.Model):
    _name = "product.template.configration"

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