# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class ProductionPlaningAPI(http.Controller):

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
            "date": rec.date or False,
            "fabric_vendor": rec.fabric_vendor_id.display_name if rec.fabric_vendor_id else "",
            "sort_no": rec.product_id.display_name if rec.product_id else "",
            "fabric_item": rec.fabric_item or "",
            "fabric_colour": rec.fabric_colour_id.display_name if rec.fabric_colour_id else "",
            "qty": rec.qty or 0.0,
            "style_no": rec.style_no or "",
            "party": rec.party_id.display_name if rec.party_id else "",
            "mc": rec.product_cat_id.display_name if rec.product_cat_id else "",
            "status": rec.status or "",
            "file_received_date": rec.file_received_date or False,
            "cutting_master": rec.cutting_master_id.display_name if rec.cutting_master_id else "",
            "blanket": rec.blanket or "",
            "blanket_status": rec.blanket_status or "",
            "shrinkage_sample": rec.shrinkage_sample or "",
            "pattern": rec.pattern or "",
            "remark": rec.remark or "",
            "cutting_start_date": rec.cutting_start_date or False,
            "cutting_end_date": rec.cutting_end_date or False,
            "fabricator_name": rec.vendor_id.display_name if rec.vendor_id else "",
            "location": rec.location or "",
            "total_machines": rec.total_machines or 0,
            "heavy_machines": rec.heavy_machines or 0,
            "garment_design": rec.garment_design or "",
            "plan_date": rec.plan_date or False,
            "no_of_person": rec.no_of_person or 0,
            "no_of_qc_person": rec.no_of_qc_person or 0,
            "no_of_style": rec.no_of_style or 0,
            "total_qty": rec.total_qty or 0.0,
            "status_by_qc": rec.status_by_qc or "",
            "status_date": rec.status_date or False,
            "qc_status": rec.qc_status or "",
            "next_week_remark": rec.next_week_remark or "",
            "required_qty_vendor": rec.required_qty_vendor or "",
            "next_week_plan": rec.next_week_plan or "",
            "next_week_qty": rec.next_week_qty or 0.0,

            "fabric_short_no": rec.short_no or "",
            "fabric_qty": rec.fabric_qty or 0.0,
            "purchase_order_no": rec.purchase_order_no or "",
            "sample": rec.sample or "",
            "labtest": rec.labtest or "",
            "pps": rec.pps or "",

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
            "col_13": rec.col_13 or "",
            "col_14": rec.col_14 or "",

            "note_1": rec.note_1 or "",
            "note_2": rec.note_2 or "",
            "note_3": rec.note_3 or "",
            "note_4": rec.note_4 or "",
            "note_5": rec.note_5 or "",
            "note_6": rec.note_6 or "",
            "note_7": rec.note_7 or "",
            "note_8": rec.note_8 or "",
            "note_9": rec.note_9 or "",
            "note_10": rec.note_10 or "",
            "note_11": rec.note_11 or "",
            "note_12": rec.note_12 or "",
            "note_13": rec.note_13 or "",
            "note_14": rec.note_14 or "",

            "active": rec.active or False,
        }

    @http.route('/api/production_planing/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_production_planing(self, **kwargs):
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

            if data.get("fabric_vendor_id"):
                domain.append(("fabric_vendor_id", "=", data.get("fabric_vendor_id")))

            if data.get("vendor_id"):
                domain.append(("vendor_id", "=", data.get("vendor_id")))

            if data.get("product_cat_id"):
                domain.append(("product_cat_id", "=", data.get("product_cat_id")))

            if data.get("fabric_colour_id"):
                domain.append(("fabric_colour_id", "=", data.get("fabric_colour_id")))

            if data.get("cutting_master_id"):
                domain.append(("cutting_master_id", "=", data.get("cutting_master_id")))

            if data.get("status"):
                domain.append(("status", "=", data.get("status")))

            if data.get("status_by_qc"):
                domain.append(("status_by_qc", "=", data.get("status_by_qc")))

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

            limit = int(data.get("limit", 80))
            offset = int(data.get("offset", 0))

            model = request.env["production.planing"].with_user(user)
            records = model.search(domain, order="id desc")
            total = model.search_count(domain)

            return self._json_response(
                True,
                "Production planing list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_record(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)