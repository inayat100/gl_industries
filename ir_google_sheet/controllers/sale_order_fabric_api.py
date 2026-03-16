# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class SalesOrderFabricAPI(http.Controller):

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
            "record_id": rec.id,
            "is_favorite": rec.is_favorite or False,
            "header": rec.header or "",
            "sl_no": rec.sl_no or "",
            "date": rec.date or False,
            "product": rec.product_id.display_name if rec.product_id else "",
            "sorts_no": rec.sorts_no or "",
            "fabric_colour": rec.fabric_colour_id.display_name if rec.fabric_colour_id else "",
            "fabric_mill": rec.fabric_mill or "",
            "fabric_supplier": rec.vendor_id.display_name if rec.vendor_id else "",
            "qty": rec.qty or 0.0,
            "hanger_fabric": rec.hanger_fabric or "",
            "weave": rec.fit_measurement_id.display_name if rec.fit_measurement_id else "",
            "fabric_category": rec.fabric_category_id.display_name if rec.fabric_category_id else "",
            "content": rec.content or "",
            "count": rec.count or "",
            "construction": rec.construction or "",
            "weight": rec.weight or "",
            "pantone_no": rec.pantone_no or "",
            "location_rack_no": rec.location_rack_no or "",
            "merchant_1": rec.merchant_id.display_name if rec.merchant_id else "",
            "merchant_2": rec.merchant_2 or "",
            "buyer_name": rec.party_id.display_name if rec.party_id else "",
            "category": rec.product_cat_id.display_name if rec.product_cat_id else "",
            "garment_development": rec.garment_development or "",
            "status": rec.status or "",
            "status_date": rec.status_date or False,
            "remarks_1": rec.remarks_1 or "",
            "remarks_2": rec.remarks_2 or "",
            "remark_date": rec.remark_date or False,
            "style_no": rec.style_no or "",

            "col_1": rec.col_1 or "",
            "col_2": rec.col_2 or "",
            "col_3": rec.col_3 or "",
            "col_4": rec.col_4 or "",
            "col_5": rec.col_5 or "",
            "col_6": rec.col_6 or "",
            "col_7": rec.col_7 or "",
            "col_8": rec.col_8 or "",
            "col_9": rec.col_9 or "",
            "col_10": rec.col_10 or "",
            "col_11": rec.col_11 or "",
            "col_12": rec.col_12 or "",

            "active": rec.active or False,
        }

    @http.route('/api/sales_order_fabric/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_sales_order_fabric(self, **kwargs):
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

            if data.get("product_id"):
                domain.append(("product_id", "=", data.get("product_id")))

            if data.get("fabric_colour_id"):
                domain.append(("fabric_colour_id", "=", data.get("fabric_colour_id")))

            if data.get("vendor_id"):
                domain.append(("vendor_id", "=", data.get("vendor_id")))

            if data.get("fit_measurement_id"):
                domain.append(("fit_measurement_id", "=", data.get("fit_measurement_id")))

            if data.get("fabric_category_id"):
                domain.append(("fabric_category_id", "=", data.get("fabric_category_id")))

            if data.get("merchant_id"):
                domain.append(("merchant_id", "=", data.get("merchant_id")))

            if data.get("party_id"):
                domain.append(("party_id", "=", data.get("party_id")))

            if data.get("product_cat_id"):
                domain.append(("product_cat_id", "=", data.get("product_cat_id")))

            if data.get("status"):
                domain.append(("status", "=", data.get("status")))

            if data.get("active") in [True, False]:
                domain.append(("active", "=", data.get("active")))

            if data.get("date_from"):
                if not self._validate_date(data.get("date_from")):
                    return self._json_response(False, "date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("date", ">=", data.get("date_from")))

            if data.get("date_to"):
                if not self._validate_date(data.get("date_to")):
                    return self._json_response(False, "date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("date", "<=", data.get("date_to")))

            if data.get("status_date_from"):
                if not self._validate_date(data.get("status_date_from")):
                    return self._json_response(False, "status_date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("status_date", ">=", data.get("status_date_from")))

            if data.get("status_date_to"):
                if not self._validate_date(data.get("status_date_to")):
                    return self._json_response(False, "status_date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("status_date", "<=", data.get("status_date_to")))

            if data.get("remark_date_from"):
                if not self._validate_date(data.get("remark_date_from")):
                    return self._json_response(False, "remark_date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("remark_date", ">=", data.get("remark_date_from")))

            if data.get("remark_date_to"):
                if not self._validate_date(data.get("remark_date_to")):
                    return self._json_response(False, "remark_date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("remark_date", "<=", data.get("remark_date_to")))

            limit = int(data.get("limit", 80))
            offset = int(data.get("offset", 0))

            model = request.env["sales.order.fabric"].with_user(user)
            records = model.search(domain, order="id desc")
            total = model.search_count(domain)

            return self._json_response(
                True,
                "Sales order fabric list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_record(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)