# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class JobWorkIssueLineAPI(http.Controller):

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
        return {
            "record_id": line.id,

            "job_work_line_id": line.job_work_line_id.id if line.job_work_line_id else False,
            "job_work_line": line.job_work_line_id.display_name if line.job_work_line_id else "",

            "vendor": line.vendor_id.display_name if line.vendor_id else "",
            "issued_qty": line.issued_qty or 0.0,
            "received_qty": line.received_qty or 0.0,
            "issue_date": line.issue_date or False,
            "user_issue_date": line.user_issue_date or False,
            "expected_date": line.expected_date or False,
            "days_to_complete": line.days_to_complete or 0,
            "rate": line.rate or 0.0,
            "amount": line.amount or 0.0,
            "pending_qty": line.pending_qty or 0.0,
            "status": line.status or "",
            "last_receipt_date": line.last_receipt_date or False,
            "remarks": line.remarks or "",
            "remark_1": line.remark_1 or "",
            "remark_2": line.remark_2 or "",
            "remark_3": line.remark_3 or "",
            "remark_date": line.remark_date or False,

            "mo_id": line.mo_id.id if line.mo_id else False,
            "mo_number": line.mo_id.display_name if line.mo_id else "",
            "bom": line.bom_id.display_name if line.bom_id else "",
            "job_work_expected_date": line.job_work_expected_date or False,
            "date_start": line.date_start or False,
            "product_qty": line.product_qty or 0.0,
            "product": line.product_id.display_name if line.product_id else "",
            "category": line.categ_id.display_name if line.categ_id else "",
            "mrp": line.mrp or 0.0,
            "brand": line.brand_id.display_name if line.brand_id else "",
            "process": line.process_id.display_name if line.process_id else "",
        }

    @http.route('/api/job_work_issue_line/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_job_work_issue_line(self, **kwargs):
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

            if data.get("job_work_line_id"):
                domain.append(("job_work_line_id", "=", data.get("job_work_line_id")))

            if data.get("vendor_id"):
                domain.append(("vendor_id", "=", data.get("vendor_id")))

            if data.get("mo_id"):
                domain.append(("mo_id", "=", data.get("mo_id")))

            if data.get("product_id"):
                domain.append(("product_id", "=", data.get("product_id")))

            if data.get("brand_id"):
                domain.append(("brand_id", "=", data.get("brand_id")))

            if data.get("process_id"):
                domain.append(("process_id", "=", data.get("process_id")))

            if data.get("status"):
                domain.append(("status", "=", data.get("status")))

            if data.get("date_from"):
                if not self._validate_date(data.get("date_from")):
                    return self._json_response(False, "date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("issue_date", ">=", data.get("date_from")))

            if data.get("date_to"):
                if not self._validate_date(data.get("date_to")):
                    return self._json_response(False, "date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("issue_date", "<=", data.get("date_to")))

            limit = int(data.get("limit", 80))
            offset = int(data.get("offset", 0))

            model = request.env["job.work.issue.line"].with_user(user)
            records = model.search(domain, order="id desc")
            total = model.search_count(domain)

            return self._json_response(
                True,
                "Job work issue line list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_line(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)