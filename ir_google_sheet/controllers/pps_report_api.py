# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class PPSLabLineAPI(http.Controller):

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

    def _serialize_line(self, line):
        parent = line.pps_lab_id

        return {
            "record_id": line.id,

            "pps_lab_id": parent.id if parent else False,
            "pps_lab_number": parent.name if parent else "",
            "parent_date": line.parent_date or False,
            "valid_upto": line.valid_upto or False,

            "document_type": line.document_type or "",
            "document_type_name": line.document_type_id.display_name if line.document_type_id else "",
            "party": line.party_id.display_name if line.party_id else "",
            "po_no": line.po_no or "",
            "new_po_no": line.new_po_no or "",
            "article_no": line.article_no or "",
            "article_url": line.article_url or "",
            "new_article_no": line.new_article_no or "",
            "po_url": line.po_url or "",
            "color": line.color_id.display_name if line.color_id else "",
            "mc": line.product_cat_id.display_name if line.product_cat_id else "",
            "mrp": line.mrp or 0.0,
            "season": line.season_id.display_name if line.season_id else "",
            "merchant": line.merchant_id.display_name if line.merchant_id else "",
            "style_no": line.product_id.display_name if line.product_id else "",
            "parent_remark": line.remark or "",
            "route": line.route_id.display_name if line.route_id else "",
            "brand": line.brand_id.display_name if line.brand_id else "",
            "receive_date": parent.receive_date if parent else False,
            "sending_date": parent.sending_date if parent else False,
            "active": parent.active if parent else False,

            "process": line.process_id.display_name if line.process_id else "",
            "description": line.name or "",
            "col1": line.col1 or "",
            "col2": line.col2 or "",
            "col3": line.col3 or "",
            "col4": line.col4 or "",
            "detail": line.detail or "",
            "line_date": line.date or False,
            "remark1": line.remark1 or "",
            "remark2": line.remark2 or "",
            "remark3": line.remark3 or "",
            "remark4": line.remark4 or "",
        }

    @http.route('/api/pps_lab_line/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_pps_lab_line(self, **kwargs):
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

            if data.get("pps_lab_id"):
                domain.append(("pps_lab_id", "=", data.get("pps_lab_id")))

            if data.get("process_id"):
                domain.append(("process_id", "=", data.get("process_id")))

            if data.get("party_id"):
                domain.append(("party_id", "=", data.get("party_id")))

            if data.get("product_id"):
                domain.append(("product_id", "=", data.get("product_id")))

            if data.get("brand_id"):
                domain.append(("brand_id", "=", data.get("brand_id")))

            if data.get("document_type"):
                domain.append(("document_type", "=", data.get("document_type")))

            if data.get("date_from"):
                if not self._validate_date(data.get("date_from")):
                    return self._json_response(False, "date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("parent_date", ">=", data.get("date_from")))

            if data.get("date_to"):
                if not self._validate_date(data.get("date_to")):
                    return self._json_response(False, "date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("parent_date", "<=", data.get("date_to")))

            records = request.env["pps.lab.line"].with_user(user).search(
                domain, order="id desc"
            )
            total = request.env["pps.lab.line"].with_user(user).search_count(domain)

            return self._json_response(
                True,
                "PPS lab line list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_line(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)