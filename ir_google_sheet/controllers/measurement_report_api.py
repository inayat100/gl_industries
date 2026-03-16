# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import http
from odoo.http import request


class MeasurementReportLineAPI(http.Controller):

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

        db = request.db
        credential = {'login': username, 'password': password, 'type': 'password'}
        # uid = request.session.authenticate(db, credential)

        credential = {'login': username, 'password': password, 'type': 'password'}
        uid = request.session.authenticate(request.db, credential)
        print("$$$$$$$$$$$$$$$", uid)
        if not uid:
            return False, "Invalid username or password."

        user = request.env['res.users'].sudo().browse(uid.get('uid'))
        return user, False

    def _serialize_line(self, line):
        measurement = line.measurement_id

        return {
            "record_id": line.id,
            "measurement_id": measurement.id if measurement else False,
            "measurement_name": measurement.name if measurement else "",
            "measurement_date": measurement.date if measurement else False,
            "fabricator_name": measurement.fabricator_name_id.display_name if measurement and measurement.fabricator_name_id else "",
            "stage": measurement.stage_id.display_name if measurement and measurement.stage_id else "",
            "debit": measurement.debit if measurement else "",
            "qty": measurement.qty if measurement else 0.0,
            "master_name": measurement.master_name_id.display_name if measurement and measurement.master_name_id else "",
            "style_no": measurement.product_id.display_name if measurement and measurement.product_id else "",
            "mc": measurement.product_cat_id.display_name if measurement and measurement.product_cat_id else "",
            "brand": measurement.brand_id.display_name if measurement and measurement.brand_id else "",
            "mrp": measurement.mrp if measurement else 0.0,
            "d_no": measurement.d_no if measurement else "",
            "party": measurement.party_id.display_name if measurement and measurement.party_id else "",
            "status": measurement.status if measurement else "",
            "delivery_date": measurement.delivery_date if measurement else False,
            "measurement_remark": measurement.remark if measurement else "",
            "measurement_remark1": measurement.remark1 if measurement else "",
            "route": measurement.route_id.display_name if measurement and measurement.route_id else "",
            "active": measurement.active if measurement else False,
            "color": measurement.color_id.display_name if measurement and measurement.color_id else "",
            "washing": measurement.washing_item_id.display_name if measurement and measurement.washing_item_id else "",
            "vendor_name": measurement.vendor_name if measurement else "",
            "process": line.process_id.display_name if line.process_id else "",
            "tol": line.tol or "",
            "line_remark": line.remark or "",
            "size1": line.size1 or "",
            "year1": line.year1 or "",
            "year2": line.year2 or "",
            "year3": line.year3 or "",
            "size2": line.size2 or "",
            "year4": line.year4 or "",
            "year5": line.year5 or "",
            "year6": line.year6 or "",
            "size3": line.size3 or "",
            "year7": line.year7 or "",
            "year8": line.year8 or "",
            "year9": line.year9 or "",
            "size4": line.size4 or "",
            "year10": line.year10 or "",
            "year11": line.year11 or "",
            "year12": line.year12 or "",
            "size5": line.size5 or "",
            "year13": line.year13 or "",
            "year14": line.year14 or "",
            "year15": line.year15 or "",
            "note1": line.note1 or "",
            "note2": line.note2 or "",
            "report_date": line.report_date or False,
        }

    @http.route('/api/measurement_report_line/list', type='http', auth='public', methods=['POST'], csrf=False)
    def list_measurement_report_line(self, **kwargs):
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

            if data.get("date_from"):
                if not self._validate_date(data.get("date_from")):
                    return self._json_response(False, "date_from must be in YYYY-MM-DD format", code=400)
                domain.append(("report_date", ">=", data.get("date_from")))

            if data.get("date_to"):
                if not self._validate_date(data.get("date_to")):
                    return self._json_response(False, "date_to must be in YYYY-MM-DD format", code=400)
                domain.append(("report_date", "<=", data.get("date_to")))

            records = request.env["measurement.report.line"].with_user(user).search(
                domain, order="id desc"
            )
            total = request.env["measurement.report.line"].with_user(user).search_count(domain)

            return self._json_response(
                True,
                "Measurement report line list fetched successfully.",
                {
                    "count": len(records),
                    "total": total,
                    "JsonDataTable": [self._serialize_line(rec) for rec in records]
                }
            )

        except Exception as e:
            return self._json_response(False, str(e), code=500)