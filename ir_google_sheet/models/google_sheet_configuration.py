from odoo import models, fields, _, api
import logging
import gspread
from odoo.exceptions import UserError
import os
from odoo.modules.module import get_module_resource
from google.oauth2.service_account import Credentials

_logger = logging.getLogger(__name__)

class GoogleSheetConfiguration(models.Model):
    _name = "google.sheet.configuration"

    spreadsheet_id = fields.Char(string="Spreadsheet ID")
    name = fields.Char(string="Name")
    spreadsheet_state = fields.Selection([('not_connect', 'Not Connected'), ('connect', 'Connected')], default='not_connect')
    sheet_ids = fields.One2many("google.sheet", "google_sheet_configuration_id", string="Sheets")


    def _get_google_client(self):
        """
        Return authorized gspread client using service account json file.
        """
        scope = [
            "https://www.googleapis.com/auth/spreadsheets"
        ]

        # JSON file should be inside your module folder or an absolute secure path
        service_file = get_module_resource(
            'ir_google_sheet',
            'static',
            'src',
            'json',
            'odoo_google_api.json'
        )
        if not service_file or not os.path.exists(service_file):
            raise UserError(_("Google API credential file not found."))

        # service_file = "/path/to/odoo_google_api.json"

        creds = Credentials.from_service_account_file(service_file, scopes=scope)
        client = gspread.authorize(creds)
        return client

    def test_spreadsheet_connection(self):
        for rec in self:
            if not rec.spreadsheet_id:
                rec.spreadsheet_state = 'not_connect'
                raise UserError(_("Please enter Spreadsheet ID first."))

            try:
                client = rec._get_google_client()
                spreadsheet = client.open_by_key(rec.spreadsheet_id)
                rec.name = spreadsheet.title
                spreadsheet.worksheets()
                rec.spreadsheet_state = 'connect'

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Spreadsheet connected successfully: %s') % spreadsheet.title,
                        'type': 'success',
                        'sticky': False,
                        'next': {'type': 'ir.actions.act_window_close'}
                    }
                }

            except Exception as e:
                _logger.exception("Google Spreadsheet connection failed")
                rec.spreadsheet_state = 'not_connect'
                raise UserError(_("Google Spreadsheet connection failed.\n\n%s") % str(e))


