from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta


class RecordLockMixin(models.AbstractModel):
    _name = "record.lock.mixin"
    _description = "Record Lock Validation Mixin"

    def _get_lock_config(self):
        """Fetch the config for the current model"""
        return self.env['record.lock.config'].search([('model_name', '=', self._name)], limit=1)

    def _check_lock(self, operation):
        config = self._get_lock_config()
        if not config:
            return  # no config → no restriction

        today = date.today()

        # Date field dynamic pick
        field_name = config.date_field_id.name
        for rec in self:
            record_date = rec[field_name]
            if config.base_on_date:
                lock_create_before = config.lock_create_before
                lock_create_after = config.lock_create_after
                lock_edit_before = config.lock_edit_before
                lock_edit_after = config.lock_edit_after
                lock_delete_before = config.lock_delete_before
                lock_delete_after = config.lock_delete_after
            else:
                lock_create_before = today - timedelta(days=config.lock_create_before_day) if config.lock_create_before_day > 0 else False
                lock_create_after = today + timedelta(days=config.lock_create_after_day) if config.lock_create_after_day > 0 else False
                lock_edit_before = today - timedelta(days=config.lock_edit_before_day) if config.lock_edit_before_day > 0 else False
                lock_edit_after = today + timedelta(days=config.lock_edit_after_day) if config.lock_edit_after_day > 0 else False
                lock_delete_before = today - timedelta(days=config.lock_delete_before_day) if config.lock_delete_before_day > 0 else False
                lock_delete_after = today + timedelta(days=config.lock_delete_after_day) if config.lock_delete_after_day > 0 else False
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
        records._check_lock("create")
        return records

    def write(self, vals):
        res = super().write(vals)
        self._check_lock("write")
        return res

    def unlink(self):
        self._check_lock("unlink")
        return super().unlink()
