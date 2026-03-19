from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from google.oauth2.service_account import Credentials
from markupsafe import Markup
import requests
import gspread
import os
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class GoogleSheet(models.Model):
    _name = "google.sheet"
    _description = "Google Sheet"

    name = fields.Char(string="Name")
    google_sheet_id = fields.Char(string="Sheet Id")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('connect', 'Connected'),
        ('failed', 'Failed')
    ], default='draft')
    report_configuration_id = fields.Many2one(
        "api.report.configuration",
        string="Report Configuration"
    )
    google_sheet_configuration_id = fields.Many2one(
        "google.sheet.configuration",
        string="Sheet Configuration"
    )
    sheet_line_ids = fields.One2many(
        "google.sheet.line",
        "google_sheet_id",
        string="Sheet Lines"
    )
    filter_line_ids = fields.One2many(
        "google.sheet.filter.line",
        "google_sheet_id",
        string="Filter Lines"
    )
    mode = fields.Selection([
        ('update', 'Update'),
        ('replace', 'Replace')
    ], default='replace', required=True, string="Mode")
    match_field = fields.Many2one(
        "google.sheet.line",
        string="Match Field",
        domain="[('google_sheet_id', '=', id)]"
    )
    json_data = fields.Json(string="Json Data")
    json_data_text = fields.Text(
        string="JSON Data Preview",
        compute="_compute_json_data_text"
    )
    json_data_html = fields.Html(
        string="JSON Table Preview",
        compute="_compute_json_data_html",
        sanitize=False
    )

    auto_sync = fields.Boolean(string="Auto Sync")
    sync_interval_number = fields.Integer(string="Sync Every", default=1)
    sync_interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
    ], string="Interval Unit", default='hours')
    next_sync_at = fields.Datetime(string="Next Sync At")
    last_sync_at = fields.Datetime(string="Last Sync At", readonly=True)
    last_sync_status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string="Last Sync Status", readonly=True)
    last_sync_message = fields.Text(string="Last Sync Message", readonly=True)
    active = fields.Boolean(string="Active", default=True)

    @api.depends("json_data")
    def _compute_json_data_text(self):
        for rec in self:
            if rec.json_data:
                rec.json_data_text = json.dumps(rec.json_data, indent=4, ensure_ascii=False)
            else:
                rec.json_data_text = False

    @api.depends("json_data")
    def _compute_json_data_html(self):
        for rec in self:
            rec.json_data_html = False
            data = rec.json_data

            if not data:
                continue

            if isinstance(data, dict):
                rows = [data]
            elif isinstance(data, list):
                rows = [row for row in data if isinstance(row, dict)]
            else:
                rec.json_data_html = Markup("<p>Unsupported JSON format</p>")
                continue

            if not rows:
                rec.json_data_html = Markup("<p>No tabular data found</p>")
                continue

            headers = []
            seen = set()
            for row in rows:
                for key in row.keys():
                    if key not in seen:
                        seen.add(key)
                        headers.append(key)

            html = """
                <div style="overflow:auto; max-width:100%;">
                    <table style="border-collapse:collapse; width:100%; font-size:13px;">
                        <thead>
                            <tr>
            """

            for head in headers:
                html += f"""
                    <th style="border:1px solid #ccc; padding:8px; background:#f5f5f5; text-align:left; white-space:nowrap;">
                        {head}
                    </th>
                """

            html += """
                            </tr>
                        </thead>
                        <tbody>
            """

            for row in rows:
                html += "<tr>"
                for head in headers:
                    value = row.get(head, "")
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    elif value is None:
                        value = ""
                    else:
                        value = str(value)

                    html += f"""
                        <td style="border:1px solid #ccc; padding:8px; vertical-align:top;">
                            {value}
                        </td>
                    """
                html += "</tr>"

            html += """
                        </tbody>
                    </table>
                </div>
            """

            rec.json_data_html = Markup(html)

    def _detect_domain_type_from_value(self, value):
        if isinstance(value, bool):
            return False

        if isinstance(value, (int, float)):
            return 'number'

        if isinstance(value, str):
            if value.strip():
                return 'name'
            return False

        return False

    def _create_filter_value_records(self, parsed_data, created_sheet_lines):
        self.ensure_one()

        FilterValue = self.env['google.sheet.filter.value']
        FilterValue.search([('google_sheet_id', '=', self.id)]).unlink()

        line_map = {line.field_name: line for line in created_sheet_lines}
        field_buckets = {}

        for row in parsed_data:
            if not isinstance(row, dict):
                continue

            for field_name, raw_value in row.items():
                sheet_line = line_map.get(field_name)
                if not sheet_line:
                    continue

                domain_type = self._detect_domain_type_from_value(raw_value)
                if not domain_type:
                    continue

                value_str = "" if raw_value is None else str(raw_value).strip()
                if not value_str:
                    continue

                field_key = (field_name, domain_type)
                bucket = field_buckets.setdefault(field_key, set())

                if len(bucket) >= 200:
                    continue

                bucket.add(value_str)

        vals_list = []
        for (field_name, domain_type), values in field_buckets.items():
            sheet_line = line_map.get(field_name)
            if not sheet_line:
                continue

            for value_str in sorted(values):
                vals_list.append({
                    'google_sheet_id': self.id,
                    'sheet_line_id': sheet_line.id,
                    'field_name': field_name,
                    'domain_type': domain_type,
                    'name': value_str,
                })

        if vals_list:
            FilterValue.create(vals_list)

    def _detect_field_domain_type(self, field_name, parsed_data):
        for row in parsed_data:
            if not isinstance(row, dict):
                continue

            value = row.get(field_name)

            if isinstance(value, bool):
                continue

            if isinstance(value, (int, float)):
                return 'number'

            if isinstance(value, str) and value.strip():
                return 'name'

        return False

    def _fetch_raw_api_data(self):
        self.ensure_one()

        configuration = self.report_configuration_id
        if not configuration:
            raise UserError(_("Please select Report Configuration first."))

        if not configuration.server_url:
            raise UserError(_("Server URL is missing in Report Configuration."))


        if configuration.is_odoo:
            today = datetime.today().strftime("%Y-%m-%d")
            headers = {
                "Content-Type": "application/json",
            }

            payload = {
                "username": configuration.user_name or "",
                "password": configuration.api_key or "",
                "date_from": str(configuration.period_from) if configuration.period_from else "",
                "date_to": str(configuration.period_to or today) if (configuration.period_to or today) else "",

            }

            response = requests.post(
                configuration.server_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            json_response = response.json()
            json_table = json_response.get('data').get('JsonDataTable')
            if not json_table:
                raise UserError(_("JsonDataTable not found in API response."))

            parsed_data = json.loads(json_table) if isinstance(json_table, str) else json_table
        else:
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            headers = {
                'username': configuration.user_name or '',
                'apikey': configuration.api_key or '',
                'company_id': configuration.company_key or '',
                'enterprise_id': configuration.enterprise_id or '',
                'user_id': configuration.user_id or '',
                'Content-Type': 'application/json',
            }

            payload = {
                "report_type": configuration.report_type,
                "filter_data": {
                    "period_from": {"value": configuration.period_from},
                    "period_to": {"value": configuration.period_to or today},
                    "location": {"value": configuration.location or ''},
                }
            }

            response = requests.post(
                configuration.server_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            json_response = response.json()
            json_table = json_response.get('JsonDataTable')
            if not json_table:
                raise UserError(_("JsonDataTable not found in API response."))

            parsed_data = json.loads(json_table) if isinstance(json_table, str) else json_table

        if not parsed_data:
            raise UserError(_("No data found in API response."))

        if isinstance(parsed_data, dict):
            parsed_data = [parsed_data]

        if not isinstance(parsed_data, list):
            raise UserError(_("Parsed API data format is invalid. Expected list or dict."))

        return parsed_data

    def action_test_api_connection(self):
        self.ensure_one()

        parsed_data = self._fetch_raw_api_data()
        self.json_data = parsed_data

        self.sheet_line_ids.unlink()
        self.filter_line_ids.unlink()
        self.env['google.sheet.filter.value'].search([
            ('google_sheet_id', '=', self.id)
        ]).unlink()
        vals_list = []
        data_keys = []
        seen = set()

        if isinstance(parsed_data, list):
            for row in parsed_data:
                if isinstance(row, dict):
                    for key in row.keys():
                        if key not in seen:
                            seen.add(key)
                            data_keys.append(key)
        elif isinstance(parsed_data, dict):
            for key in parsed_data.keys():
                if key not in seen:
                    seen.add(key)
                    data_keys.append(key)
        for key in data_keys:
            domain_type = self._detect_field_domain_type(key, parsed_data)
            vals_list.append({
                'google_sheet_id': self.id,
                'field_name': key,
                'field_head': key,
                'domain_type': domain_type,
            })

        created_lines = self.env['google.sheet.line']
        if vals_list:
            created_lines = self.env['google.sheet.line'].create(vals_list)
        if created_lines:
            self._create_filter_value_records(parsed_data, created_lines)
        self.state = 'connect'

    def test_api_connection(self):
        self.action_test_api_connection()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('API connected successfully and sheet lines generated.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

    def _get_google_client(self):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets"
        ]

        service_file = get_module_resource(
            'ir_google_sheet',
            'static',
            'src',
            'json',
            'odoo_google_api.json'
        )
        if not service_file or not os.path.exists(service_file):
            raise UserError(_("Google API credential file not found."))

        creds = Credentials.from_service_account_file(service_file, scopes=scope)
        client = gspread.authorize(creds)
        return client

    def _get_or_create_worksheet(self, spreadsheet):
        self.ensure_one()
        worksheet = None

        if self.google_sheet_id:
            try:
                worksheet = spreadsheet.get_worksheet_by_id(int(self.google_sheet_id))
            except Exception:
                worksheet = None

        if not worksheet:
            worksheet = spreadsheet.add_worksheet(
                title=self.name or "Sheet1",
                rows=1000,
                cols=100
            )
            self.google_sheet_id = str(worksheet.id)
            self.active = True
        return worksheet

    def _prepare_selected_lines(self):
        self.ensure_one()

        selected_lines = self.sheet_line_ids.filtered(
            lambda l: l.add_sheet and l.field_name and l.col_name
        )

        if not selected_lines:
            raise UserError(_("Please configure at least one sheet line with Add enabled, Field Name and Col Name."))

        used_cols = set()
        for line in selected_lines:
            col = (line.col_name or '').strip().upper()
            if col in used_cols:
                raise UserError(_("Duplicate column name found: %s") % col)
            used_cols.add(col)
        return selected_lines

    def _prepare_api_data(self):
        self.ensure_one()
        parsed_data = self._fetch_raw_api_data()
        self.json_data = parsed_data
        parsed_data = self._apply_filters_to_parsed_data(parsed_data)
        print("parsed_data=========", parsed_data)
        return parsed_data

    def _convert_value(self, value):
        # dict / list → JSON string
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        # None → empty
        if value is None:
            return ""

        # 🔥 Formula → return as-is
        if isinstance(value, str) and value.startswith("="):
            return value

        # 🔥 Numbers → keep as number (IMPORTANT)
        if isinstance(value, (int, float)):
            return value

        # 🔥 Boolean
        if isinstance(value, bool):
            return value

        # बाकी sab → string
        return str(value)

    def _index_to_column_letter(self, index):
        result = ""
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def _column_letter_to_index(self, col_name):
        col_name = (col_name or '').strip().upper()
        if not col_name:
            raise UserError(_("Column Name is required."))

        result = 0
        for char in col_name:
            if not ('A' <= char <= 'Z'):
                raise UserError(_("Invalid column name: %s") % col_name)
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result

    def _build_header_row(self, selected_lines):
        selected_lines = selected_lines.sorted(
            key=lambda l: self._column_letter_to_index(l.col_name)
        )
        return [line.field_head or line.field_name for line in selected_lines]

    def _build_data_rows(self, parsed_data, selected_lines):
        selected_lines = selected_lines.sorted(
            key=lambda l: self._column_letter_to_index(l.col_name)
        )

        data_rows = []
        for row in parsed_data:
            if not isinstance(row, dict):
                continue

            row_values = []
            for line in selected_lines:
                if line.is_formula and line.formula:
                    value = line.formula
                else:
                    value = row.get(line.field_name, "")
                row_values.append(self._convert_value(value))
            data_rows.append(row_values)
        return data_rows

    def _replace_sheet_data(self, worksheet, parsed_data, selected_lines):
        selected_lines = selected_lines.sorted(
            key=lambda l: self._column_letter_to_index(l.col_name)
        )

        max_col_index = 0
        for line in selected_lines:
            col_index = self._column_letter_to_index(line.col_name)
            if col_index > max_col_index:
                max_col_index = col_index

        final_values = []

        header_row = [""] * max_col_index
        for line in selected_lines:
            col_index = self._column_letter_to_index(line.col_name) - 1
            header_row[col_index] = line.field_head or line.field_name
        final_values.append(header_row)

        for record in parsed_data:
            if not isinstance(record, dict):
                continue

            row_data = [""] * max_col_index
            for line in selected_lines:
                col_index = self._column_letter_to_index(line.col_name) - 1
                if line.is_formula and line.formula:
                    value = line.formula
                else:
                    value = record.get(line.field_name, "")
                row_data[col_index] = self._convert_value(value)
            final_values.append(row_data)
        # ===== FORMULA BASED SUM =====

        sum_columns = []
        for line in selected_lines:
            if line.is_sum:
                col_index = self._column_letter_to_index(line.col_name) - 1
                sum_columns.append((col_index, line))

        if sum_columns and final_values:
            sum_row = [""] * len(final_values[0])

            total_rows = len(final_values)  # header included

            for col_index, line in sum_columns:
                col_letter = line.col_name.upper()

                # Formula: SUM from row 2 to last data row
                # sum_row[col_index] = f"=SUM({col_letter}2:{col_letter}{total_rows})"
                data_start_row = 3
                last_row = len(final_values) + 1

                if last_row >= data_start_row:
                    sum_row[col_index] = f"=SUM({col_letter}{data_start_row}:{col_letter}{last_row})"

            sum_row[0] = "Total"

            final_values.append(sum_row)

        # ===== END =====
        worksheet.clear()
        end_col = self._index_to_column_letter(max_col_index)
        end_row = len(final_values)
        # worksheet.update(f'A1:{end_col}{end_row}', final_values)
        start_row = 2
        end_row = len(final_values) + 1

        worksheet.update(
            f"A{start_row}:{end_col}{end_row}",
            final_values,
            value_input_option="USER_ENTERED"
        )
        worksheet.set_basic_filter(f"A2:{end_col}{end_row}")
        worksheet.freeze(rows=2)

    def _ensure_headers_by_col_name(self, worksheet, selected_lines):
        all_values = worksheet.get_all_values()
        # existing_header = all_values[0] if all_values else []

        existing_header = all_values[1] if len(all_values) > 1 else []

        max_col_index = 0
        for line in selected_lines:
            col_index = self._column_letter_to_index(line.col_name)
            if col_index > max_col_index:
                max_col_index = col_index

        if len(existing_header) < max_col_index:
            existing_header += [""] * (max_col_index - len(existing_header))

        for line in selected_lines:
            col_index = self._column_letter_to_index(line.col_name) - 1
            existing_header[col_index] = line.field_head or line.field_name

        end_col = self._index_to_column_letter(len(existing_header))
        # worksheet.update(f'A1:{end_col}1', [existing_header])
        worksheet.update(
            f'A2:{end_col}2',
            [existing_header],
            value_input_option="USER_ENTERED"
        )

        return existing_header

    def _build_row_updates_by_col_name(self, record, selected_lines):
        row_updates = {}
        for line in selected_lines:
            col_index = self._column_letter_to_index(line.col_name) - 1
            if line.is_formula and line.formula:
                value = line.formula
            else:
                value = record.get(line.field_name, "")
            row_updates[col_index] = self._convert_value(value)
        return row_updates

    def _update_row_preserve_columns(self, worksheet, row_no, row_updates, required_len):
        existing_row = worksheet.row_values(row_no)

        if len(existing_row) < required_len:
            existing_row += [""] * (required_len - len(existing_row))

        for col_index, value in row_updates.items():
            existing_row[col_index] = value

        end_col = self._index_to_column_letter(len(existing_row))
        worksheet.update(f'A{row_no}:{end_col}{row_no}', [existing_row])

    def _update_sheet_data(self, worksheet, parsed_data, selected_lines):
        self.ensure_one()

        selected_lines = selected_lines.sorted(
            key=lambda l: self._column_letter_to_index(l.col_name)
        )

        existing_values = worksheet.get_all_values()
        existing_row_count = len(existing_values) if existing_values else 0

        # header ko existing sheet ke base par preserve karo
        # existing_header = list(existing_values[0]) if existing_values else []
        existing_header = list(existing_values[1]) if len(existing_values) > 1 else []

        max_col_index = max(self._column_letter_to_index(l.col_name) for l in selected_lines)

        if len(existing_header) < max_col_index:
            existing_header += [""] * (max_col_index - len(existing_header))

        # selected columns ke headers hi update hon
        for line in selected_lines:
            col_index = self._column_letter_to_index(line.col_name) - 1
            existing_header[col_index] = line.field_head or line.field_name

        final_values = [existing_header]

        # existing data rows preserve structure
        for idx, record in enumerate(parsed_data, start=1):
            if idx < len(existing_values):
                # row_data = list(existing_values[idx])
                row_data = list(existing_values[idx + 1]) if len(existing_values) > idx + 1 else []
            else:
                row_data = []

            if len(row_data) < len(existing_header):
                row_data += [""] * (len(existing_header) - len(row_data))

            for line in selected_lines:
                col_index = self._column_letter_to_index(line.col_name) - 1
                if line.is_formula and line.formula:
                    value = line.formula
                else:
                    value = record.get(line.field_name, "")
                row_data[col_index] = self._convert_value(value)

            final_values.append(row_data)

        # ===== FORMULA BASED SUM =====

        sum_columns = []
        for line in selected_lines:
            if line.is_sum:
                col_index = self._column_letter_to_index(line.col_name) - 1
                sum_columns.append((col_index, line))

        if sum_columns and final_values:
            sum_row = [""] * len(final_values[0])

            total_rows = len(final_values)  # header included

            for col_index, line in sum_columns:
                col_letter = line.col_name.upper()

                # Formula: SUM from row 2 to last data row
                data_start_row = 3
                last_row = len(final_values) + 1

                sum_row[col_index] = f"=SUM({col_letter}{data_start_row}:{col_letter}{last_row})"
                # sum_row[col_index] = f"=SUM({col_letter}2:{col_letter}{total_rows})"

            sum_row[0] = "Total"

            final_values.append(sum_row)

        # ===== END =====

        # first update selected data with preserved other columns
        end_col = self._index_to_column_letter(len(existing_header))
        new_row_count = len(final_values)
        # worksheet.update(f"A1:{end_col}{new_row_count}", final_values)
        start_row = 2
        end_row = len(final_values) + 1

        worksheet.update(
            f"A{start_row}:{end_col}{end_row}",
            final_values,
            value_input_option="USER_ENTERED"
        )
        worksheet.set_basic_filter(f"A2:{end_col}{end_row}")
        worksheet.freeze(rows=2)
        # extra old rows me sirf selected columns clear karo
        if existing_row_count > new_row_count:
            clear_requests = []
            for line in selected_lines:
                col_name = (line.col_name or '').strip().upper()
                clear_requests.append(
                    f"{col_name}{new_row_count + 1}:{col_name}{existing_row_count}"
                )
            if clear_requests:
                worksheet.batch_clear(clear_requests)

    def _get_next_sync_time(self, from_time=None):
        self.ensure_one()
        from_time = from_time or fields.Datetime.now()

        interval_number = self.sync_interval_number or 1

        if self.sync_interval_type == 'minutes':
            return from_time + timedelta(minutes=interval_number)
        elif self.sync_interval_type == 'hours':
            return from_time + timedelta(hours=interval_number)
        elif self.sync_interval_type == 'days':
            return from_time + timedelta(days=interval_number)

        return from_time + timedelta(hours=1)

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.auto_sync and not rec.next_sync_at:
            rec.next_sync_at = fields.Datetime.now()
        return rec

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if vals.get('auto_sync') is True and not rec.next_sync_at:
                rec.next_sync_at = fields.Datetime.now()
            elif vals.get('auto_sync') is False:
                rec.next_sync_at = False
            if 'name' in vals and rec.google_sheet_id and rec.google_sheet_configuration_id and rec.google_sheet_configuration_id.spreadsheet_id:
                try:
                    client = rec._get_google_client()
                    spreadsheet = client.open_by_key(rec.google_sheet_configuration_id.spreadsheet_id)
                    worksheet = spreadsheet.get_worksheet_by_id(int(rec.google_sheet_id))
                    worksheet.update_title(rec.name)
                except Exception as e:
                    _logger.exception("Failed to auto rename worksheet for %s", rec.display_name)
        return res

    def _sync_google_sheet(self):
        self.ensure_one()

        if not self.google_sheet_configuration_id or not self.google_sheet_configuration_id.spreadsheet_id:
            self.state = 'failed'
            raise UserError(_("Please set Spreadsheet ID in Google Sheet Configuration."))

        selected_lines = self._prepare_selected_lines()
        parsed_data = self._prepare_api_data()

        client = self._get_google_client()
        spreadsheet = client.open_by_key(self.google_sheet_configuration_id.spreadsheet_id)
        worksheet = self._get_or_create_worksheet(spreadsheet)

        if self.mode == 'replace':
            self._replace_sheet_data(worksheet, parsed_data, selected_lines)
        else:
            self._update_sheet_data(worksheet, parsed_data, selected_lines)

        self.state = 'connect'
        return True

    def action_send_data(self):
        self.ensure_one()

        try:
            self._sync_google_sheet()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Data sent to Google Sheet successfully.'),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'}
                }
            }

        except Exception as e:
            _logger.exception("Failed to send data to Google Sheet")
            self.state = 'failed'
            raise UserError(_("Failed to send data to Google Sheet.\n\n%s") % str(e))

    def cron_sync_google_sheets(self):
        now = fields.Datetime.now()

        sheets = self.search([
            ('auto_sync', '=', True),
            ('next_sync_at', '!=', False),
            ('next_sync_at', '<=', now),
        ])

        for sheet in sheets:
            try:
                sheet._sync_google_sheet()
                sheet.write({
                    'last_sync_at': now,
                    'last_sync_status': 'success',
                    'last_sync_message': 'Synced successfully',
                    'next_sync_at': sheet._get_next_sync_time(now),
                    'state': 'connect',
                })
            except Exception as e:
                _logger.exception("Google Sheet sync failed for %s", sheet.display_name)
                sheet.write({
                    'last_sync_at': now,
                    'last_sync_status': 'failed',
                    'last_sync_message': str(e),
                    'next_sync_at': sheet._get_next_sync_time(now),
                    'state': 'failed',
                })

    def action_delete_google_sheet(self):
        self.ensure_one()

        if not self.google_sheet_configuration_id or not self.google_sheet_configuration_id.spreadsheet_id:
            raise UserError(_("Spreadsheet ID not found in Google Sheet Configuration."))

        if not self.google_sheet_id:
            raise UserError(_("No Google worksheet is linked with this record."))

        try:
            client = self._get_google_client()
            spreadsheet = client.open_by_key(self.google_sheet_configuration_id.spreadsheet_id)

            worksheet = None
            try:
                worksheet = spreadsheet.get_worksheet_by_id(int(self.google_sheet_id))
            except Exception:
                worksheet = None

            if not worksheet:
                raise UserError(_("Worksheet not found in Google Spreadsheet."))

            spreadsheet.del_worksheet(worksheet)

            self.write({
                'google_sheet_id': False,
                'active': False,
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Google Sheet deleted successfully.'),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'}
                }
            }

        except Exception as e:
            _logger.exception("Failed to delete Google Sheet")
            self.state = 'failed'
            raise UserError(_("Failed to delete Google Sheet.\n\n%s") % str(e))

    def action_rename_google_sheet(self):
        self.ensure_one()

        if not self.google_sheet_configuration_id or not self.google_sheet_configuration_id.spreadsheet_id:
            raise UserError(_("Spreadsheet ID not found in Google Sheet Configuration."))

        if not self.google_sheet_id:
            raise UserError(_("No Google worksheet is linked with this record."))

        if not self.name:
            raise UserError(_("Please set sheet name first."))

        try:
            client = self._get_google_client()
            spreadsheet = client.open_by_key(self.google_sheet_configuration_id.spreadsheet_id)
            worksheet = spreadsheet.get_worksheet_by_id(int(self.google_sheet_id))

            worksheet.update_title(self.name)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Google worksheet renamed successfully.'),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'}
                }
            }

        except Exception as e:
            _logger.exception("Failed to rename Google Sheet")
            raise UserError(_("Failed to rename Google worksheet.\n\n%s") % str(e))

    def _apply_filters_to_parsed_data(self, parsed_data):
        self.ensure_one()

        filter_lines = self.filter_line_ids.filtered(
            lambda f: f.active and f.sheet_line_id and f.domain_type
        )

        if not filter_lines:
            return parsed_data

        filtered_data = []

        for row in parsed_data:
            if not isinstance(row, dict):
                continue

            matched = True

            for flt in filter_lines:
                field_name = flt.sheet_line_id.field_name
                row_value = row.get(field_name)
                if flt.domain_type == 'name':
                    # ✅ ADD THIS BLOCK HERE
                    if flt.operator == 'is_set':
                        if row_value in (None, '', False):
                            matched = False
                            break
                        continue

                    if flt.operator == 'is_not_set':
                        if row_value not in (None, '', False):
                            matched = False
                            break
                        continue

                    row_text = "" if row_value is None else str(row_value).strip()
                    selected_values = flt.suggested_value_ids.mapped('name')

                    if not selected_values and flt.value_text:
                        selected_values = [flt.value_text.strip()]

                    selected_values = [v.strip() for v in selected_values if v and v.strip()]

                    if not selected_values:
                        continue

                    if flt.operator == '=':
                        if row_text not in selected_values:
                            matched = False
                            break

                    elif flt.operator == '!=':
                        if row_text in selected_values:
                            matched = False
                            break

                    elif flt.operator == 'contains':
                        if not any(val.lower() in row_text.lower() for val in selected_values):
                            matched = False
                            break

                    elif flt.operator == 'not_contains':
                        if any(val.lower() in row_text.lower() for val in selected_values):
                            matched = False
                            break
                elif flt.domain_type == 'number':
                    try:
                        if row_value in (None, ''):
                            matched = False
                            break

                        row_num = float(row_value)
                        filter_num = float(flt.value_number)
                    except Exception:
                        matched = False
                        break

                    if flt.number_operator == '=':
                        if row_num != filter_num:
                            matched = False
                            break

                    elif flt.number_operator == '!=':
                        if row_num == filter_num:
                            matched = False
                            break

                    elif flt.number_operator == '>':
                        if row_num <= filter_num:
                            matched = False
                            break

                    elif flt.number_operator == '<':
                        if row_num >= filter_num:
                            matched = False
                            break

                    elif flt.number_operator == '>=':
                        if row_num < filter_num:
                            matched = False
                            break

                    elif flt.number_operator == '<=':
                        if row_num > filter_num:
                            matched = False
                            break

            if matched:
                filtered_data.append(row)

        return filtered_data

    def action_send_data_old(self):
        self.ensure_one()

        if not self.google_sheet_configuration_id or not self.google_sheet_configuration_id.spreadsheet_id:
            self.state = 'failed'
            raise UserError(_("Please set Spreadsheet ID in Google Sheet Configuration."))

        try:
            selected_lines = self._prepare_selected_lines()
            parsed_data = self._prepare_api_data()

            client = self._get_google_client()
            spreadsheet = client.open_by_key(self.google_sheet_configuration_id.spreadsheet_id)
            worksheet = self._get_or_create_worksheet(spreadsheet)

            if self.mode == 'replace':
                self._replace_sheet_data(worksheet, parsed_data, selected_lines)
            else:
                self._update_sheet_data(worksheet, selected_lines, parsed_data)

            self.state = 'connect'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Data sent to Google Sheet successfully.'),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'}
                }
            }

        except Exception as e:
            _logger.exception("Failed to send data to Google Sheet")
            self.state = 'failed'
            raise UserError(_("Failed to send data to Google Sheet.\n\n%s") % str(e))