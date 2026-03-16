# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class SamplePlaningAPI(http.Controller):

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
            "date": rec.date or False,
            "is_favorite": rec.is_favorite or False,

            "product": rec.product_id.display_name if rec.product_id else "",
            "party": rec.party_id.display_name if rec.party_id else "",
            "mc": rec.product_cat_id.display_name if rec.product_cat_id else "",
            "mrp": rec.mrp or 0.0,
            "spec": rec.spec or "",
            "fabric": rec.fabric or "",
            "fabric_supplier": rec.vendor_id.display_name if rec.vendor_id else "",
            "washing_partner": rec.washing_id.display_name if rec.washing_id else "",
            "washing": rec.washing or "",
            "merchant": rec.merchant_id.display_name if rec.merchant_id else "",
            "merchant_comment": rec.merchant_comment or "",
            "merchant_1_comment": rec.merchant_1_comment or "",
            "spc_pfd": rec.spc_pfd or "",
            "tec_pack": rec.tec_pack or "",
            "reference": rec.ref or "",
            "sample_qty": rec.sample_qty or 0.0,
            "status": rec.status or "",
            "status_date": rec.status_date or False,
            "delivery_date": rec.delivery_date or False,

            "col_1": rec.col_1 or "",
            "col_2": rec.col_2 or "",
            "col_3": rec.col_3 or "",
            "col_4": rec.col_4 or "",
            "col_5": rec.col_5 or False,
            "col_6": rec.col_6 or False,

            "fabric_book_date": rec.fabric_book_date or False,
            "fabric_received_date": rec.fabric_received_date or False,
            "fabric_received_status": rec.fabric_received_status or "",

            "trims_book_date": rec.trims_book_date or False,
            "trims_received_date": rec.trims_received_date or False,
            "trims_received_status": rec.trims_received_status or "",

            "trims_1_book_date": rec.trims_1_book_date or False,
            "trims_1_received_date": rec.trims_1_received_date or False,
            "trims_1_received_status": rec.trims_1_received_status or "",

            "trims_2_book_date": rec.trims_2_book_date or False,
            "trims_2_received_date": rec.trims_2_received_date or False,
            "trims_2_received_status": rec.trims_2_received_status or "",

            "trims_3_book_date": rec.trims_3_book_date or False,
            "trims_3_received_date": rec.trims_3_received_date or False,
            "trims_3_received_status": rec.trims_3_received_status or "",

            "trims_4_book_date": rec.trims_4_book_date or False,
            "trims_4_received_date": rec.trims_4_received_date or False,
            "trims_4_received_status": rec.trims_4_received_status or "",

            "cutting_book_date": rec.cutting_book_date or False,
            "cutting_received_date": rec.cutting_received_date or False,
            "cutting_received_status": rec.cutting_received_status or "",

            "stitching_book_date": rec.stitching_book_date or False,
            "stitching_received_date": rec.stitching_received_date or False,
            "stitching_received_status": rec.stitching_received_status or "",

            "print_book_date": rec.print_book_date or False,
            "print_received_date": rec.print_received_date or False,
            "print_received_status": rec.print_received_status or "",

            "emb_book_date": rec.emb_book_date or False,
            "emb_received_date": rec.emb_received_date or False,
            "emb_received_status": rec.emb_received_status or "",

            "washing_book_date": rec.washing_book_date or False,
            "washing_received_date": rec.washing_received_date or False,
            "washing_received_status": rec.washing_received_status or "",

            "finishing_book_date": rec.finishing_book_date or False,
            "finishing_received_date": rec.finishing_received_date or False,
            "finishing_received_status": rec.finishing_received_status or "",

            "packing_book_date": rec.packing_book_date or False,
            "packing_received_date": rec.packing_received_date or False,
            "packing_received_status": rec.packing_received_status or "",

            "delivery_book_date": rec.delivery_book_date or False,
            "delivery_received_date": rec.delivery_received_date or False,
            "delivery_received_status": rec.delivery_received_status or "",

            "active": rec.active or False,
        }

    @http.route('/api/sample_planing/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_sample_planing(self, **kwargs):
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

            if data.get("party_id"):
                domain.append(("party_id", "=", data.get("party_id")))

            if data.get("product_cat_id"):
                domain.append(("product_cat_id", "=", data.get("product_cat_id")))

            if data.get("vendor_id"):
                domain.append(("vendor_id", "=", data.get("vendor_id")))

            if data.get("washing_id"):
                domain.append(("washing_id", "=", data.get("washing_id")))

            if data.get("merchant_id"):
                domain.append(("merchant_id", "=", data.get("merchant_id")))

            if data.get("status"):
                domain.append(("status", "=", data.get("status")))

            if data.get("fabric_received_status"):
                domain.append(("fabric_received_status", "=", data.get("fabric_received_status")))

            if data.get("trims_received_status"):
                domain.append(("trims_received_status", "=", data.get("trims_received_status")))

            if data.get("cutting_received_status"):
                domain.append(("cutting_received_status", "=", data.get("cutting_received_status")))

            if data.get("stitching_received_status"):
                domain.append(("stitching_received_status", "=", data.get("stitching_received_status")))

            if data.get("print_received_status"):
                domain.append(("print_received_status", "=", data.get("print_received_status")))

            if data.get("emb_received_status"):
                domain.append(("emb_received_status", "=", data.get("emb_received_status")))

            if data.get("washing_received_status"):
                domain.append(("washing_received_status", "=", data.get("washing_received_status")))

            if data.get("finishing_received_status"):
                domain.append(("finishing_received_status", "=", data.get("finishing_received_status")))

            if data.get("packing_received_status"):
                domain.append(("packing_received_status", "=", data.get("packing_received_status")))

            if data.get("delivery_received_status"):
                domain.append(("delivery_received_status", "=", data.get("delivery_received_status")))

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

            if data.get("delivery_date_from"):
                if not self._validate_date(data.get("delivery_date_from")):
                    return self._json_response(False, "delivery_date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("delivery_date", ">=", data.get("delivery_date_from")))

            if data.get("delivery_date_to"):
                if not self._validate_date(data.get("delivery_date_to")):
                    return self._json_response(False, "delivery_date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("delivery_date", "<=", data.get("delivery_date_to")))

            limit = int(data.get("limit", 80))
            offset = int(data.get("offset", 0))

            model = request.env["sample.planing"].with_user(user)
            records = model.search(domain, order="id desc")
            total = model.search_count(domain)

            return self._json_response(
                True,
                "Sample planing list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_record(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)