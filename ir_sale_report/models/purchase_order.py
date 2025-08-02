from odoo import models, fields, api
from datetime import datetime
import requests
import json
from odoo.osv import expression

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    voucher_id = fields.Char(string="Voucher Id")
    voucher_number = fields.Char(string="Voucher No")
    api_order = fields.Boolean(string="API Order")
    remark_1 = fields.Char(string="Remark1")
    remark_2 = fields.Char(string="Remark2")
    remark_3 = fields.Char(string="Remark3")
    remark_4 = fields.Char(string="Remark4")

    def custom_button_confirm(self):
        ctx = dict(self.env.context)
        self.with_context(ctx).button_confirm()
        self.action_validate_picking()

    def _cron_create_purchase_order(self):
        configration_ids = self.env['purchase.order.configration'].search([('active', '=', True)])
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
                response = requests.post(url, json=payload, headers=headers)
                print("response", response)
                json_response = response.json()
                parsed_data = json.loads(json_response['JsonDataTable'])
                test_json = [parsed_data[0]]
                product_id = self.env['product.product']
                uom_id = self.env['uom.uom']
                tax_ids = self.env['account.tax']
                for data in parsed_data:
                    try:
                        val = {
                            'api_order': True,
                            'voucher_id': data.get('voucher_id'),
                            'voucher_number': data.get('Voucher_Number'),
                            'notes': data.get('Narration'),
                            'partner_ref': data.get('Reference_Number'),
                            'origin': data.get('document_udf1')
                        }
                        if configration.company_id:
                            val['company_id'] = configration.company_id.id
                        if data.get('Party'):
                            partner_id = self._get_create_partner(data.get('Party'), data.get('GST_No'))
                            val['partner_id'] = partner_id.id
                            if partner_id:
                                d_partner_id = self._get_create_delivery_partner(partner_id, data.get('Contact_Person'), data.get('GST_No'))
                                if d_partner_id:
                                    val['dest_address_id'] = d_partner_id.id
                        if data.get('Voucher_Date'):
                            order_date = self.parse_iso_date(data.get('Voucher_Date'))
                            if order_date:
                                val['date_order'] = order_date
                        order_id = self.env['purchase.order'].search([('voucher_id', '=', data.get('voucher_id'))], limit=1)
                        if order_id:
                            order_id.write(val)
                        else:
                            order_id = self.env['purchase.order'].create([val])
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
                            'product_qty': product_uom_qty,
                            'price_unit': price_unit,
                            'product_uom':uom_id.id
                        }
                        exist_line = self._get_order_exist_line(data.get('voucher_id'),product_id, product_uom_qty, price_unit)
                        if exist_line:
                            exist_line.write(line)
                        else:
                            line['order_id'] = order_id.id
                            self.env['purchase.order.line'].create(line)
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
        line_ids = self.env['purchase.order.line'].search([('voucher_id', '=', voucher_id)])
        for res in line_ids:
            if res.product_id.id == product_id.id and res.product_qty == product_uom_qty and res.price_unit == price_unit:
                return res
            return False
        return False

    def action_validate_picking(self):
        draft_picking = self.picking_ids.filtered(lambda p: p.state in ['draft', 'waiting', 'confirmed', 'assigned'])
        if len(draft_picking) == 1:
            for move in draft_picking.move_ids_without_package:
                if move.product_id.tracking == 'lot':
                    lot_name = move.purchase_line_id.lot_name
                    for line in  move.move_line_ids:
                        if not lot_name:
                            lot_name = self.env['ir.sequence'].next_by_code('stock.move.line.lot.name')
                        line.lot_name = lot_name
        draft_picking.button_validate()

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'po'), ('user_id', '=', self.env.user.id)], limit=1)
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
        if view_type in ["form", "list"]:
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'po'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("invisible", "1")
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

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    voucher_id = fields.Char(string="Voucher Id")
    lot_name = fields.Char(string="Lot Name")

    @api.depends_context('company')
    @api.depends('product_id')
    def _compute_display_name(self):
        for line in self:
            line.display_name = f"[{line.order_id.voucher_number}] {line.product_id.name} {line.order_id.partner_ref}"

    @api.model
    def _search_display_name(self, operator, value):
        name = value or ''
        if operator in ('=', '!='):
            domain = ['|', '|',  ('order_id.voucher_number', '=', name.split(' ')[0]), ('name', operator, name), ('order_id.partner_ref', operator, name)]
        else:
            domain = ['|', '|',  ('order_id.voucher_number', '=like', name.split(' ')[0] + '%'), ('name', operator, name), ('order_id.partner_ref', operator, name)]
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = ['&', '!'] + domain[1:]
        return domain




class PurchaseOrderConfigration(models.Model):
    _name = "purchase.order.configration"

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