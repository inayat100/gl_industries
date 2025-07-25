from odoo import models, fields
from datetime import datetime
import requests
import json

class SaleOrder(models.Model):
    _inherit = "sale.order"


    voucher_id = fields.Char(string="Voucher Id")
    voucher_number = fields.Char(string="Voucher No")
    api_order = fields.Boolean(string="API Order")


    def _cron_create_sale_order(self):
        configration_ids = self.env['sale.order.configration'].search([('active', '=', True)])
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for configration in configration_ids:
            if configration:
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
                print("@@@@@@@@@@@@@", payload)
                response = requests.post(url, json=payload, headers=headers)
                json_response = response.json()
                parsed_data = json.loads(json_response['JsonDataTable'])
                test_json = [parsed_data[0]]
                product_id = self.env['product.product']
                uom_id = self.env['uom.uom']
                tax_ids = self.env['account.tax']
                print("parsed_data====", len(parsed_data))
                for data in parsed_data:
                    try:
                        val = {
                            'api_order': True,
                            'voucher_id': data.get('voucher_id'),
                            'voucher_number': data.get('Voucher_Number'),
                            'note': data.get('Narration')
                        }
                        if configration.company_id:
                            val['company_id'] = configration.company_id.id
                        if data.get('Party'):
                            partner_id = self._get_create_partner(data.get('Party'), data.get('GST_No'))
                            val['partner_id'] = partner_id.id
                            if partner_id:
                                d_partner_id = self._get_create_delivery_partner(partner_id, data.get('Contact_Person'), data.get('GST_No'))
                                if d_partner_id:
                                    val['partner_shipping_id'] = d_partner_id.id
                        if data.get('Voucher_Date'):
                            order_date = self.parse_iso_date(data.get('Voucher_Date'))
                            if order_date:
                                val['date_order'] = order_date
                        order_id = self.env['sale.order'].search([('voucher_id', '=', data.get('voucher_id'))], limit=1)
                        if order_id:
                            order_id.write(val)
                        else:
                            order_id = self.env['sale.order'].create([val])
                        # line data form here
                        if data.get('Item'):
                            product_id = product_id.search([('name', '=', data.get('Item'))], limit=1)
                            if product_id:
                                product_id = product_id
                        if data.get('Unit'):
                            uom_id = uom_id.search([('name', '=', data.get('Unit'))], limit=1)
                            if uom_id:
                                uom_id = uom_id
                        if data.get('Tax_Code'):
                            tax_ids = tax_ids.search([('type_tax_use', '=', 'sale'), ('name', '=', data.get('Tax_Code'))])
                            if tax_ids:
                                pass
                        product_uom_qty = data.get('Qty')
                        price_unit = data.get('Rate')
                        line = {
                            'voucher_id': data.get('voucher_id'),
                            'product_id': product_id.id,
                            'name': product_id.name or 'Not Found Product',
                            'product_uom_qty': product_uom_qty,
                            'price_unit': price_unit,
                            'product_uom':uom_id.id
                        }
                        exist_line = self._get_order_exist_line(data.get('voucher_id'), product_id, product_uom_qty, price_unit)
                        if exist_line:
                            exist_line.write(line)
                        else:
                            line['order_id'] = order_id.id
                            self.env['sale.order.line'].create(line)
                    except Exception as e:
                        print("Erroes", e)

    def parse_iso_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date() if date_str else False
        except Exception:
            return False

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

    def _get_create_delivery_partner(self, parent_id, name, address=None, gst=False):
        partner_id = self.env['res.partner'].search([('parent_id', '=', parent_id.id), ('name', '=', name)], limit=1)
        if partner_id:
            return partner_id
        else:
            partner_id = self.env['res.partner'].create([{
                'name': name,
                'parent_id': parent_id.id,
                'vat': gst
            }])
            return partner_id

    def _get_order_exist_line(self, voucher_id, product_id, product_uom_qty, price_unit):
        line_ids = self.env['sale.order.line'].search([('voucher_id', '=', voucher_id)])
        for res in line_ids:
            if res.product_id.id == product_id.id and res.product_uom_qty == product_uom_qty and res.price_unit == price_unit:
                return res
            return False
        return False

    def action_confirm(self):
        res = super().action_confirm()
        for mo in self.mrp_production_ids:
            mo.sale_order_id = self.id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    voucher_id = fields.Char(string="Voucher Id")


class SaleOrderConfigration(models.Model):
    _name = "sale.order.configration"

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
