from odoo import models, fields

class ApiReportConfiguration(models.Model):
    _name = "api.report.configuration"

    name = fields.Char(string="Name", copy=False, required=1)
    is_odoo = fields.Boolean(string="With Odoo", default=False)
    server_url = fields.Char(string="Server Url", default="http://163.53.86.110:9700/ABReportService.svc/GetReportData", required=1)
    user_name = fields.Char(string="Username", default="glrs.smiley@gmail.com", required=1)
    api_key = fields.Char(string="Api Key", default="93c3d155-16c6-4ce8-88a6-8cdc6ae47e42", required=1)
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, required=1)
    company_key = fields.Char(string="Company Id", default="891aeb06-0a19-4288-b3a3-dade3e637d75", required=1)
    enterprise_id = fields.Char(string="Enterprise Id", default="ae465013-0e51-44e6-b9f9-8e6c0eba5ebd", required=1)
    user_id = fields.Char(string="User Id", default="4ba51619-3efc-4302-84a3-22e220d1b27e", required=1)
    report_type = fields.Integer("Report Type", required=1)
    period_from = fields.Char(string="Period From", help="YYYY-MM-DD 00:00:00", default="2024-05-01 00:11:00")
    period_to = fields.Char(string="Period To", help="YYYY-MM-DD 00:00:00", default="2024-05-01 00:11:00")
    active = fields.Boolean(string="Active", default=True)
    location = fields.Char(string="Location", default='')