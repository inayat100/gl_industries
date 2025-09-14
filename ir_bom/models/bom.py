from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    product_cat_id = fields.Many2one("product.category", string="MC")
    brand_id = fields.Many2one("brand.master", string="Brand")
    product_design_type_id = fields.Many2one("product.design.type", string="Product Type")
    color_id = fields.Many2one("color.master", string="Color")
    mrp = fields.Float(string="MRP")
    mrp_production_ids = fields.Many2many("mrp.production", compute="_compute_mrp_production_ids")
    mrp_production_count = fields.Integer( compute="_compute_mrp_production_ids", string="MO")
    state = fields.Selection([('open', 'Open'),('running', 'Running'), ('closed', 'Closed')], string="State", compute="_compute_mrp_state", store=True)
    date = fields.Date(string="Date", default=fields.date.today())
    route_id = fields.Many2one("bom.route", string="Route")
    remark1 = fields.Char(string="Remark 1")
    remark2 = fields.Char(string="Remark 2")

    def _compute_mrp_production_ids(self):
        for res in self:
            mrp_ids = self.env['mrp.production'].search([('bom_id', '=', res.id)])
            res.mrp_production_ids = mrp_ids.ids
            if mrp_ids:
                res.mrp_production_count = len(mrp_ids)
            else:
                res.mrp_production_count = 0

    @api.depends('mrp_production_ids')
    def _compute_mrp_state(self):
        for res in self:
            running_state_list = res.mrp_production_ids.filtered(lambda m:m.state in ['draft', 'confirmed', 'progress'])
            closed_state_list = res.mrp_production_ids.filtered(lambda m:m.state in ['to_close', 'done', 'cancel'])
            if running_state_list:
                res.state = 'running'
            elif closed_state_list:
                res.state = 'closed'
            else:
                res.state = 'open'

    @api.onchange('product_id', 'product_tmpl_id')
    def _onchange_product_id(self):
        self.product_cat_id = self.product_id.categ_id.id or self.product_tmpl_id.categ_id.id
        self.brand_id = self.product_id.brand_id.id or self.product_tmpl_id.brand_id.id
        self.product_design_type_id = self.product_id.product_design_type_id.id or self.product_tmpl_id.product_design_type_id.id
        self.color_id = self.product_id.color_id.id or self.product_tmpl_id.color_id.id
        self.mrp = self.product_id.mrp or self.product_tmpl_id.mrp

    @api.onchange('route_id')
    def _onchange_route_id(self):
        self.date = self.route_id.date
        if self.bom_line_ids:
            self.bom_line_ids = [(5, 0, 0)]
        lines = []
        for line in self.route_id.line_ids:
            lines.append((0, 0, {
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'note': line.note,
                'qty_per_pack': line.qty_per_pack,
                'qty_percent': line.qty_percent,
                'rate': line.rate,
                'amount': line.amount,
                'qty_in_pack': line.qty_in_pack,
                'color_id': line.color_id.id,
                'size_id': line.size_id.id,
                'vendor_id': line.vendor_id.id,
                'remark': line.remark,
            }))
        self.bom_line_ids = lines

    @api.onchange('product_qty')
    def _onchange_line_product_qty(self):
        for line in self.bom_line_ids:
            if line.qty_in_pack > 0:
                qty_per_pack = self.product_qty / line.qty_in_pack
            else:
                qty_per_pack = 0.0
            qty_percent = (qty_per_pack * line.extra_per) / 100
            line.qty_per_pack = qty_per_pack
            line.qty_percent = qty_percent
            line.product_qty = qty_per_pack + qty_percent

    def action_view_mo_orders(self):
        self.ensure_one()
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(self.mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.mrp_production_ids[0].id,
            })
        else:
            action.update({
                'name': _("Manufacturing Orders from %s", self.product_id.name),
                'domain': [('id', 'in', self.mrp_production_ids.ids)],
                'view_mode': 'list,form',
            })
        return action

    def _get_lock_config(self, user_id):
        """Fetch the config for the current model"""
        return self.env['record.lock.config'].search([('model_name', '=', self._name), ('user_id', '=', user_id.id)],
                                                     limit=1)

    def _normalize_date(self, value):
        """Ensure we always compare as date."""
        if isinstance(value, datetime):
            return value.date()
        return value

    def _check_lock(self, operation, user_id):
        config = self._get_lock_config(user_id)
        if not config or not config.date_field_id:
            return

        # Date field dynamic pick
        field_name = config.date_field_id.name
        today = date.today()
        for rec in self:
            record_date = rec[field_name]
            record_date = self._normalize_date(record_date)
            if config.base_on_date:
                lock_create_before = config.lock_create_before
                lock_create_after = config.lock_create_after
                lock_edit_before = config.lock_edit_before
                lock_edit_after = config.lock_edit_after
                lock_delete_before = config.lock_delete_before
                lock_delete_after = config.lock_delete_after
            else:
                if config.lock_create_before_day == 0:
                    lock_create_before = today
                else:
                    lock_create_before = today - timedelta(
                        days=config.lock_create_before_day) if config.lock_create_before_day > 0 else False
                if config.lock_create_after_day == 0:
                    lock_create_after = today
                else:
                    lock_create_after = today + timedelta(
                        days=config.lock_create_after_day) if config.lock_create_after_day > 0 else False
                if config.lock_edit_before_day == 0:
                    lock_edit_before = today
                else:
                    lock_edit_before = today - timedelta(
                        days=config.lock_edit_before_day) if config.lock_edit_before_day > 0 else False
                if config.lock_edit_after_day == 0:
                    lock_edit_after = today
                else:
                    lock_edit_after = today + timedelta(
                        days=config.lock_edit_after_day) if config.lock_edit_after_day > 0 else False
                if config.lock_delete_before_day == 0:
                    lock_delete_before = today
                else:
                    lock_delete_before = today - timedelta(
                        days=config.lock_delete_before_day) if config.lock_delete_before_day > 0 else False
                if config.lock_delete_after_day == 0:
                    lock_delete_after = today
                else:
                    lock_delete_after = today + timedelta(
                        days=config.lock_delete_after_day) if config.lock_delete_after_day > 0 else False
            if not record_date:
                continue  # skip if no date set
            if lock_create_before and lock_create_after:
                if operation == "create" and record_date < lock_create_before or record_date > lock_create_after:
                    raise UserError(_(
                        "You can only create %(doc)s with a date between %(start)s and %(end)s. "
                        "But you tried with date: %(given)s."
                    ) % {
                                        'doc': self._description,
                                        'start': lock_create_before,
                                        'end': lock_create_after,
                                        'given': record_date,
                                    })
            elif lock_create_before:
                if operation == "create" and record_date < lock_create_before:
                    raise UserError(_("You cannot create %s with date %s before %s") %
                                    (self._description, record_date, lock_create_before))
            elif lock_create_after:
                if operation == "create" and record_date < lock_create_after:
                    raise UserError(_("You cannot create %s with date %s after %s") %
                                    (self._description, record_date, lock_create_after))
            if lock_edit_before and lock_edit_after:
                if operation == "write" and record_date < lock_edit_before or record_date > lock_edit_after:
                    raise UserError(_(
                        "You can only write %(doc)s with a date between %(start)s and %(end)s. "
                        "But you tried with date: %(given)s."
                    ) % {
                                        'doc': self._description,
                                        'start': lock_edit_before,
                                        'end': lock_edit_after,
                                        'given': record_date,
                                    })
            elif lock_edit_before:
                if operation == "write" and record_date < lock_edit_before:
                    raise UserError(_("You cannot write %s with date %s before %s") %
                                    (self._description, record_date, lock_edit_before))
            elif lock_edit_after:
                if operation == "write" and record_date < lock_edit_after:
                    raise UserError(_("You cannot write %s with date %s after %s") %
                                    (self._description, record_date, lock_edit_after))

            if lock_delete_before and lock_delete_after:
                if operation == "unlink" and record_date < lock_delete_before or record_date > lock_delete_after:
                    raise UserError(_(
                        "You can only delete %(doc)s with a date between %(start)s and %(end)s. "
                        "But you tried with date: %(given)s."
                    ) % {
                                        'doc': self._description,
                                        'start': lock_delete_before,
                                        'end': lock_delete_after,
                                        'given': record_date,
                                    })
            elif lock_delete_before:
                if operation == "unlink" and record_date < lock_delete_before:
                    raise UserError(_("You cannot delete %s with date %s before %s") %
                                    (self._description, record_date, lock_delete_before))
            elif lock_delete_after:
                if operation == "unlink" and record_date < lock_delete_after:
                    raise UserError(_("You cannot delete %s with date %s after %s") %
                                    (self._description, record_date, lock_delete_after))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._check_lock("create", record.create_uid)
        return records

    def write(self, vals):
        res = super().write(vals)
        user = self.env.user
        self._check_lock("write", user)
        return res

    def unlink(self):
        user = self.env.user
        self._check_lock("unlink", user)
        return super().unlink()

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'mrp.bom'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.sudo().filtered(lambda l: l.is_readonly or l.is_invisible):
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
        if view_type in ["list", "form"]:
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'mrp.bom'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.sudo().line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.sudo().field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if view_type == "list":
                        if field.is_invisible:
                            field_node.set("column_invisible", "1")
                    if view_type == "form":
                        if field.is_invisible:
                            if field.field_id.model == 'mrp.bom.line':
                                field_node.set("column_invisible", "1")
                            else:
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

    def copy(self, default=None):
        report_id = self.env['api.report.configration'].search([('report_type', '=', 'mrp.bom'), ('user_id', '=', self.env.user.id)], limit=1)
        if report_id and report_id.disable_duplicate:
            raise UserError("You are not allowed to duplicate, as duplication is restricted.")
        res = super().copy(default)
        return res

    def toggle_active(self):
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'mrp.bom'), ('user_id', '=', self.env.user.id)], limit=1)
        if report_id and report_id.disable_archive:
            raise UserError("You are not allowed to archive or unarchive this record.")
        return super().toggle_active()


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    uom_id = fields.Many2one("uom.uom", string="UOM")
    note = fields.Char(string="Note")
    qty_per_pack = fields.Float(string="Qty Per Pack")
    qty_percent = fields.Float(string="Qty percent")
    extra_per = fields.Float(string="Extra Per")
    rate = fields.Float(string="Rate")
    amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
    qty_in_pack = fields.Float(string="Qty In Pack")
    color_id = fields.Many2one("color.master", string="Color")
    size_id = fields.Many2one("size.master", string="Size")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    remark = fields.Char(string="Remark")

    date = fields.Date(related="bom_id.date", string="Date", store=True)
    p_product_qty = fields.Float(related="bom_id.product_qty", string="Bom Qty", store=True)
    p_mrp = fields.Float(related="bom_id.mrp", string="Mrp", store=True)
    product_cat_id = fields.Many2one(related="bom_id.product_cat_id", string="MC", store=True)
    brand_id = fields.Many2one(related="bom_id.brand_id", string="Brand", store=True)
    state = fields.Selection(related="bom_id.state", string="State", store=True)

    @api.onchange('product_id', 'extra_per', 'qty_in_pack')
    def _onchange_qty(self):
        if self.qty_in_pack > 0:
            qty_per_pack = self.bom_id.product_qty / self.qty_in_pack
        else:
            qty_per_pack = 0.0
        qty_percent = (qty_per_pack * self.extra_per) / 100
        self.qty_per_pack = qty_per_pack
        self.qty_percent = qty_percent
        self.product_qty = qty_per_pack + qty_percent

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.uom_id = self.product_id.uom_id.id
        self.rate = self.product_id.mrp
        self.qty_in_pack = self.product_id.qty_in_pack
        self.color_id = self.product_id.color_id.id
        self.size_id = self.product_id.size_id.id

    @api.depends('rate', 'product_qty')
    def _compute_amount(self):
        for res in self:
            res.amount = res.product_qty * res.rate

    def action_view_bom_orders(self):
        self.ensure_one()
        action = {
            'res_model': 'mrp.bom',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.bom_id.id
        }
        return action

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'mrp.bom.line'), ('user_id', '=', self.env.user.id)], limit=1)
        test_list = []
        for field in report_id.line_ids.sudo().filtered(lambda l: l.is_readonly or l.is_invisible):
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
        if view_type in ["list", "form"]:
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'mrp.bom.line'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.sudo().line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.sudo().field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if view_type == "list":
                        if field.is_invisible:
                            field_node.set("column_invisible", "1")
                    if view_type == "form":
                        if field.is_invisible:
                            if field.field_id.model == 'mrp.bom.line':
                                field_node.set("column_invisible", "1")
                            else:
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