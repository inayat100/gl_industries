from odoo import models, fields
import requests
import json
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    voucher_id = fields.Char(string="Voucher Id")
    api_move = fields.Boolean(string="API Move")
    voucher_number = fields.Char(string="Voucher Number")
    ref_vno = fields.Char(string="Ref Vno")
    v_date = fields.Date(string="V Date")
    api_remark = fields.Char(string="Remark")
    detail_remark = fields.Char(string="Detail Remark")
    po_number = fields.Char(string="Po Number")
    total_bags = fields.Char(string="Total Bags")


    def _cron_create_invoice(self):
        configration = self.env['account.move.configration'].search([('type', '=', 'invoice'), ('active', '=', True)], limit=1)
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if configration:
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
            test_json = [parsed_data[0]]
            print("test_json==", test_json)
            sale_order = self.env['sale.order']
            product_id = self.env['product.product']
            uom_id = self.env['uom.uom']
            tax_ids = self.env['account.tax']
            for data in parsed_data:
                try:
                    if data.get('parent_vno'):
                        sale_order = sale_order.search([('voucher_number', '=', data.get('parent_vno'))], limit=1)
                    journal_id = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    val = {
                        'move_type': 'out_invoice',
                        'voucher_id': data.get('voucher_id'),
                        'api_move': True,
                        'journal_id': journal_id.id,
                        'voucher_number': data.get('voucher_number'),
                        'ref_vno': data.get('ref_vno'),
                        'api_remark': data.get('voucher_remark'),
                        'detail_remark': data.get('detail_remark'),
                        'po_number': data.get('document_udf1'),
                        'total_bags': data.get('document_udf2'),
                        'invoice_origin': sale_order.name or '',

                    }
                    if data.get('Party'):
                        if sale_order and sale_order.partner_id.name == data.get('Party'):
                            val['partner_id'] =  sale_order.partner_id.id
                        else:
                            partner_id = self._get_create_partner(data.get('Party'), data.get('GST_No'))
                            val['partner_id'] = partner_id.id
                    if data.get('reference_date'):
                        invoice_date = self.parse_iso_date(data.get('reference_date'))
                        val['invoice_date'] = invoice_date
                    if data.get('voucher_date'):
                        invoice_date = self.parse_iso_date(data.get('voucher_date'))
                        val['v_date'] = invoice_date
                    move_id = self.env['account.move'].search([('voucher_id', '=', data.get('voucher_id'))], limit=1)
                    if move_id:
                        move_id.write(val)
                    else:
                        move_id = self.env['account.move'].create([val])
                    if data.get('Item'):
                        product_id = product_id.search([('name', '=', data.get('Item'))], limit=1)
                        if product_id:
                            product_id = product_id
                    if data.get('unit_name'):
                        uom_id = uom_id.search([('name', '=', data.get('unit_name'))], limit=1)
                        if uom_id:
                            uom_id = uom_id
                    # if data.get('Tax_Code'):
                    #     tax_ids = tax_ids.search([('type_tax_use', '=', 'sale'), ('name', '=', data.get('Tax_Code'))])
                    #     if tax_ids:
                    #         pass
                    product_uom_qty = data.get('qty')
                    price_unit = data.get('rate')
                    account_id = self.env['account.account'].search([('name', '=', 'Local Sales')], limit=1)
                    line = {
                        'voucher_id': data.get('voucher_id'),
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'quantity': product_uom_qty,
                        'price_unit': price_unit,
                        'batch_no': data.get('batch_no'),
                        # 'account_id': account_id.id,
                        'product_uom_id': uom_id.id
                    }
                    exist_line = self._get_exist_line(data.get('voucher_id'), product_id, product_uom_qty, price_unit)
                    if exist_line:
                        exist_line.write(line)
                    else:
                        line['move_id'] = move_id.id
                        self.env['account.move.line'].create([line])
                except Exception as e:
                    print("Erroes", e)

    def _cron_create_bill(self):
        configration = self.env['account.move.configration'].search([('type', '=', 'bill'), ('active', '=', True)], limit=1)
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if configration:
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
            test_json = [parsed_data[0]]
            print("test_json==", test_json)
            purchase_order = self.env['purchase.order']
            product_id = self.env['product.product']
            uom_id = self.env['uom.uom']
            tax_ids = self.env['account.tax']
            for data in parsed_data:
                try:
                    if data.get('parent_vno'):
                        purchase_order = purchase_order.search([('voucher_number', '=', data.get('parent_vno'))], limit=1)
                    journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
                    val = {
                        'move_type': 'in_invoice',
                        'voucher_id': data.get('voucher_id'),
                        'api_move': True,
                        'journal_id': journal_id.id,
                        'voucher_number': data.get('voucher_number'),
                        'ref_vno': data.get('ref_vno'),
                        'api_remark': data.get('voucher_remark'),
                        'detail_remark': data.get('detail_remark'),
                        'po_number': data.get('document_udf1'),
                        'total_bags': data.get('document_udf2'),
                        'invoice_origin': purchase_order.name or '',

                    }
                    if data.get('Party'):
                        if purchase_order and purchase_order.partner_id.name == data.get('Party'):
                            val['partner_id'] =  purchase_order.partner_id.id
                        else:
                            partner_id = self._get_create_partner(data.get('Party'), data.get('GST_No'))
                            val['partner_id'] = partner_id.id
                    if data.get('reference_date'):
                        invoice_date = self.parse_iso_date(data.get('reference_date'))
                        val['invoice_date'] = invoice_date
                    if data.get('voucher_date'):
                        invoice_date = self.parse_iso_date(data.get('voucher_date'))
                        val['v_date'] = invoice_date
                    move_id = self.env['account.move'].search([('voucher_id', '=', data.get('voucher_id'))], limit=1)
                    if move_id:
                        move_id.write(val)
                    else:
                        move_id = self.env['account.move'].create([val])
                    if data.get('Item'):
                        product_id = product_id.search([('name', '=', data.get('Item'))], limit=1)
                        if product_id:
                            product_id = product_id
                    if data.get('unit_name'):
                        uom_id = uom_id.search([('name', '=', data.get('unit_name'))], limit=1)
                        if uom_id:
                            uom_id = uom_id
                    # if data.get('Tax_Code'):
                    #     tax_ids = tax_ids.search([('type_tax_use', '=', 'sale'), ('name', '=', data.get('Tax_Code'))])
                    #     if tax_ids:
                    #         pass
                    product_uom_qty = data.get('qty')
                    price_unit = data.get('rate')
                    # account_id = self.env['account.account'].search([('name', '=', 'Local Sales')], limit=1)
                    line = {
                        'voucher_id': data.get('voucher_id'),
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'quantity': product_uom_qty,
                        'price_unit': price_unit,
                        'batch_no': data.get('batch_no'),
                        # 'account_id': account_id.id,
                        'product_uom_id': uom_id.id
                    }
                    exist_line = self._get_exist_line(data.get('voucher_id'), product_id, product_uom_qty, price_unit)
                    if exist_line:
                        exist_line.write(line)
                    else:
                        line['move_id'] = move_id.id
                        self.env['account.move.line'].create([line])
                except Exception as e:
                    print("Erroes", e)

    def _get_create_partner(self, name, address=None, gst=False):
        partner_id = self.env['res.partner'].search([('name', '=', name)], limit=1)
        if partner_id:
            return partner_id
        else:
            partner_id = self.env['res.partner'].create([{
                'name': name,
                'vat': gst,
            }])
            return partner_id

    def parse_iso_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date() if date_str else False
        except Exception:
            return False

    def _get_exist_line(self, voucher_id, product_id, product_uom_qty, price_unit):
        line_ids = self.env['account.move.line'].search([('voucher_id', '=', voucher_id)])
        for res in line_ids:
            if res.product_id.id == product_id.id and res.quantity == product_uom_qty and res.price_unit == price_unit:
                return res
            return False
        return False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    voucher_id = fields.Char(string="Voucher Id")
    batch_no = fields.Char(string="Batch No")



class PurchaseOrderConfigration(models.Model):
    _name = "account.move.configration"

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
    type = fields.Selection([('invoice', 'Invoice'), ('bill', 'Bill')], required=True)