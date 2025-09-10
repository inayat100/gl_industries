from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    remark_1 = fields.Char(string="Remark 1")
    remark_2 = fields.Char(string="Remark 2")
    remark_3 = fields.Char(string="Remark 3")
    remark_4 = fields.Char(string="Remark 4")

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'mo'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
            if field.is_readonly:
                test_list.append(True)
            else:
                test_list.append(False)
            if field.is_invisible:
                test_list.append(True)
            else:
                test_list.append(False)
        if report_id.disable_create:
            test_list.append(True)
        else:
            test_list.append(False)
        if report_id.disable_delete:
            test_list.append(True)
        else:
            test_list.append(False)
        if report_id.disable_edit:
            test_list.append(True)
        else:
            test_list.append(False)
        test_list = tuple(test_list)
        key = key + (
            test_list,
        )
        return key

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ["form", "list"]:
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'mo'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("invisible", "1")
            if report_id.disable_create:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("create", "0")
            if report_id.disable_delete:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("delete", "0")
            if report_id.disable_edit:
                for node in arch.xpath(f"//{view_type}"):
                    node.set("edit", "0")
        return arch, view


class StockMove(models.Model):
    _inherit = "stock.move"

    purchase_order_line_id = fields.Many2one("purchase.order.line", string="Purchase Line")
    remark_1 = fields.Char(string="Remark 1")
    remark_2 = fields.Char(string="Remark 2")
    remark_3 = fields.Char(string="Remark 3")
    remark_4 = fields.Char(string="Remark 4")
