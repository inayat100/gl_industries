# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class ProductionMoveReportAPI(http.Controller):

    def _json_response(self, status=True, message="", data=None, code=200):
        body = {
            "status": status,
            "message": message,
            "data": data or {}
        }
        return request.make_response(
            json.dumps(body, default=str),
            headers=[('Content-Type', 'application/json')],
            status=code
        )

    def _validate_json(self):
        try:
            raw = request.httprequest.data.decode('utf-8') or "{}"
            return json.loads(raw), None
        except Exception as e:
            return None, str(e)

    def _validate_date(self, date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except Exception:
            return False

    def _authenticate_user(self, username, password):
        if not username or not password:
            return False, "Username and password are required."

        credential = {
            'login': username,
            'password': password,
            'type': 'password'
        }

        auth_data = request.session.authenticate(request.db, credential)
        if not auth_data:
            return False, "Invalid username or password."

        user = request.env['res.users'].sudo().browse(auth_data.get('uid'))
        if not user.exists():
            return False, "Authenticated user not found."

        return user, False

    def _serialize_record(self, rec):
        return {
            "record_id": rec.id if rec else False,
            "stock_move": rec.stock_move_id.display_name if rec.stock_move_id else "",
            "mo": rec.mo_id.display_name if rec.mo_id else "",
            "sale_order": rec.sale_id.display_name if rec.sale_id else "",
            "purchase_line": rec.purchase_line_id.display_name if rec.purchase_line_id else "",
            "component_product": rec.bom_product_id.display_name if rec.bom_product_id else "",
            "product": rec.product_id.display_name if rec.product_id else "",
            "customer": rec.so_partner_id.display_name if rec.so_partner_id else "",
            "vendor": rec.po_partner_id.display_name if rec.po_partner_id else "",
            "so_qty": rec.so_qty or 0.0,
            "po_qty": rec.po_qty or 0.0,
            "in_qty": rec.in_qty or 0.0,
            "mo_qty": rec.mo_qty or 0.0,
            "order_pending_qty": rec.order_pending_qty or 0.0,
            "in_pending_qty": rec.in_pending_qty or 0.0,
            "to_consume": rec.product_uom_qty or 0.0,

            "po_date": rec.po_date or False,
            "so_date": rec.so_date or False,

            "receipt": rec.picking_id.display_name if rec.picking_id else "",
            "receipt_ref": rec.picking_ref or "",
            "receipt_date": rec.picking_date or False,

            "p_remark_1": rec.p_remark_1 or "",
            "p_remark_2": rec.p_remark_2 or "",
            "p_remark_3": rec.p_remark_3 or "",
            "p_remark_4": rec.p_remark_4 or "",

            "c_remark_1": rec.c_remark_1 or "",
            "c_remark_2": rec.c_remark_2 or "",
            "c_remark_3": rec.c_remark_3 or "",
            "c_remark_4": rec.c_remark_4 or "",

            "mc": rec.product_cat_id.display_name if rec.product_cat_id else "",
            "mrp": rec.mrp or 0.0,
            "brand": rec.brand_id.display_name if rec.brand_id else "",
            "po_ref": rec.po_ref or "",
            "po_origin": rec.po_origin or "",
        }

    @http.route('/api/production_move_report/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_production_move_report(self, **kwargs):
        data, error = self._validate_json()
        if error:
            return self._json_response(False, "Invalid JSON payload: %s" % error, code=400)

        try:
            username = data.get("username")
            password = data.get("password")

            user, auth_error = self._authenticate_user(username, password)
            if auth_error:
                return self._json_response(False, auth_error, code=401)

            domain = []

            if data.get("id"):
                domain.append(("id", "=", data.get("id")))

            if data.get("mo_id"):
                domain.append(("mo_id", "=", data.get("mo_id")))

            if data.get("stock_move_id"):
                domain.append(("stock_move_id", "=", data.get("stock_move_id")))

            if data.get("sale_id"):
                domain.append(("sale_id", "=", data.get("sale_id")))

            if data.get("purchase_line_id"):
                domain.append(("purchase_line_id", "=", data.get("purchase_line_id")))

            if data.get("bom_product_id"):
                domain.append(("bom_product_id", "=", data.get("bom_product_id")))

            if data.get("product_id"):
                domain.append(("product_id", "=", data.get("product_id")))

            if data.get("so_partner_id"):
                domain.append(("so_partner_id", "=", data.get("so_partner_id")))

            if data.get("po_partner_id"):
                domain.append(("po_partner_id", "=", data.get("po_partner_id")))

            if data.get("picking_id"):
                domain.append(("picking_id", "=", data.get("picking_id")))

            if data.get("product_cat_id"):
                domain.append(("product_cat_id", "=", data.get("product_cat_id")))

            if data.get("brand_id"):
                domain.append(("brand_id", "=", data.get("brand_id")))

            if data.get("po_ref"):
                domain.append(("po_ref", "ilike", data.get("po_ref")))

            if data.get("po_origin"):
                domain.append(("po_origin", "ilike", data.get("po_origin")))

            if data.get("picking_ref"):
                domain.append(("picking_ref", "ilike", data.get("picking_ref")))

            if data.get("date_from"):
                if not self._validate_date(data.get("date_from")):
                    return self._json_response(False, "date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("po_date", ">=", data.get("date_from") + " 00:00:00"))

            if data.get("date_to"):
                if not self._validate_date(data.get("date_to")):
                    return self._json_response(False, "date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("po_date", "<=", data.get("date_to") + " 23:59:59"))

            if data.get("so_date_from"):
                if not self._validate_date(data.get("so_date_from")):
                    return self._json_response(False, "so_date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("so_date", ">=", data.get("so_date_from") + " 00:00:00"))

            if data.get("so_date_to"):
                if not self._validate_date(data.get("so_date_to")):
                    return self._json_response(False, "so_date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("so_date", "<=", data.get("so_date_to") + " 23:59:59"))

            if data.get("receipt_date_from"):
                if not self._validate_date(data.get("receipt_date_from")):
                    return self._json_response(False, "receipt_date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("picking_date", ">=", data.get("receipt_date_from") + " 00:00:00"))

            if data.get("receipt_date_to"):
                if not self._validate_date(data.get("receipt_date_to")):
                    return self._json_response(False, "receipt_date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("picking_date", "<=", data.get("receipt_date_to") + " 23:59:59"))

            limit = int(data.get("limit", 80))
            offset = int(data.get("offset", 0))

            model = request.env["production.move.report"].with_user(user)
            records = model.search(domain, order="id desc")
            total = model.search_count(domain)

            return self._json_response(
                True,
                "Production move report list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_record(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)