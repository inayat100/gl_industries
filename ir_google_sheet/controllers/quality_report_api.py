# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class QualityReportAPI(http.Controller):

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

    def _serialize_trims_line(self, line):
        return {
            "id": line.id,
            "name": getattr(line, 'name', '') or "",
            "process": line.process_id.display_name if getattr(line, 'process_id', False) else "",
            "remark": getattr(line, 'remark', '') or "",
            "result": getattr(line, 'result', '') or "",
            "status": getattr(line, 'status', '') or "",
        }

    def _serialize_sewing_line(self, line):
        return {
            "id": line.id,
            "name": getattr(line, 'name', '') or "",
            "process": line.process_id.display_name if getattr(line, 'process_id', False) else "",
            "remark": getattr(line, 'remark', '') or "",
            "result": getattr(line, 'result', '') or "",
            "status": getattr(line, 'status', '') or "",
        }

    def _serialize_feed_line(self, line):
        return {
            "id": line.id,
            "name": getattr(line, 'name', '') or "",
            "process": line.process_id.display_name if getattr(line, 'process_id', False) else "",
            "remark": getattr(line, 'remark', '') or "",
            "result": getattr(line, 'result', '') or "",
            "status": getattr(line, 'status', '') or "",
        }

    def _serialize_construction_line(self, line):
        return {
            "id": line.id,
            "name": getattr(line, 'name', '') or "",
            "process": line.process_id.display_name if getattr(line, 'process_id', False) else "",
            "remark": getattr(line, 'remark', '') or "",
            "result": getattr(line, 'result', '') or "",
            "status": getattr(line, 'status', '') or "",
        }

    def _serialize_quality_report(self, rec):
        return {
            "id": rec.id,
            "name": rec.name or "",
            "date": rec.date or False,
            "fabricator_name": rec.fabricator_name_id.display_name if rec.fabricator_name_id else "",
            "location": rec.location or "",
            "style_no": rec.product_id.display_name if rec.product_id else "",
            "mc": rec.product_cat_id.display_name if rec.product_cat_id else "",
            "qty": rec.qty or 0.0,
            "cutting_issue_date": rec.cutting_issue_date or False,
            "brand": rec.brand_id.display_name if rec.brand_id else "",
            "cutting_remark": rec.cutting_remark or "",
            "seller_sample": rec.seller_sample or "",
            "no_of_operator": rec.no_of_operator or "",
            "status": rec.status or "",
            "remark": rec.remark or "",
            "delivery_date": rec.delivery_date or False,
            "trims_route": rec.trims_route_id.display_name if rec.trims_route_id else "",
            "sewing_route": rec.sewing_route_id.display_name if rec.sewing_route_id else "",
            "feed_route": rec.feed_route_id.display_name if rec.feed_route_id else "",
            "construction_route": rec.construction_route_id.display_name if rec.construction_route_id else "",
            "active": rec.active,

            "trims_lines": [self._serialize_trims_line(line) for line in rec.trims_lines],
            "sewing_machine_lines": [self._serialize_sewing_line(line) for line in rec.sewing_machine_lines],
            "feed_lines": [self._serialize_feed_line(line) for line in rec.feed_lines],
            "construction_lines": [self._serialize_construction_line(line) for line in rec.construction_lines],
        }

    @http.route('/api/quality_report/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_quality_report(self, **kwargs):
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

            if data.get("fabricator_name_id"):
                domain.append(("fabricator_name_id", "=", data.get("fabricator_name_id")))

            if data.get("product_id"):
                domain.append(("product_id", "=", data.get("product_id")))

            if data.get("product_cat_id"):
                domain.append(("product_cat_id", "=", data.get("product_cat_id")))

            if data.get("brand_id"):
                domain.append(("brand_id", "=", data.get("brand_id")))

            if data.get("status"):
                domain.append(("status", "=", data.get("status")))

            if data.get("active") is not None:
                domain.append(("active", "=", data.get("active")))

            if data.get("date_from"):
                if not self._validate_date(data.get("date_from")):
                    return self._json_response(False, "date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("date", ">=", data.get("date_from")))

            if data.get("date_to"):
                if not self._validate_date(data.get("date_to")):
                    return self._json_response(False, "date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("date", "<=", data.get("date_to")))

            records = request.env["quality.report"].with_user(user).search(
                domain, order="id desc"
            )
            total = request.env["quality.report"].with_user(user).search_count(domain)

            return self._json_response(
                True,
                "Quality report list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_quality_report(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)