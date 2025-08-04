from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    sale_order_report_id = fields.Many2one("api.report.configration", string="Sale Order Report")
    sample_planning_report_id = fields.Many2one("api.report.configration", string="Sample Planning Report")
    fabric_yardage_report_id = fields.Many2one("api.report.configration", string="Fabric Yardage Report")
    production_planing_report_id = fields.Many2one("api.report.configration", string="Production Planing Report")
    component_report_report_id = fields.Many2one("api.report.configration", string="Production Planing Report")

    def action_custom_user_view(self):
        self.env['res.groups']._update_user_groups_view()

    def refresh_user_group(self, xml_id):
        """Refreshes a user's group (remove if exists, then add again)."""
        group = self.env.ref(xml_id)
        for user in self:
            if group in user.groups_id:
                # Step 1: Remove the group
                user.write({'groups_id': [(3, group.id)]})
            # Step 2: Add the group back
            user.write({'groups_id': [(4, group.id)]})