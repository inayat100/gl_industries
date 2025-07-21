from odoo import fields, models, api


class ProductionPlaning(models.Model):
    _name = 'production.planing'
    _description = 'Production Planing'

    date = fields.Date(string='Date')
    fabric_vendor_id = fields.Many2one('res.partner', string='Fabric Vendor')
    product_id = fields.Many2one("product.product", string='Sort No')
    fabric_item = fields.Char(string='Fabric Item')
    fabric_colour = fields.Char(string='Fabric Colour')
    qty = fields.Float(string='Qty')
    style_no = fields.Char(string='Style No')
    party_id = fields.Many2one('res.partner', string='Party')
    mc = fields.Many2one('product.category', string='MC')
    status = fields.Char(string='Status')
    file_received_date = fields.Date(string='File Received Date')
    cutting_master = fields.Char(string='Cutting Master')
    blanket = fields.Char(string='Blanket')
    blanket_status = fields.Char(string='Blanket Status')
    shrinkage_sample = fields.Char(string='Shrinkage Sample')
    pattern = fields.Char(string='Pattern')
    remark = fields.Char(string='Remark')
    cutting_start_date = fields.Date(string='Cutting Start Date')
    cutting_end_date = fields.Date(string='Cutting End Date')

    col_1 = fields.Char(string='Col-1')
    col_2 = fields.Char(string='Col-2')
    col_3 = fields.Char(string='Col-3')
    col_4 = fields.Char(string='Col-4')
    col_5 = fields.Char(string='Col-5')
    col_6 = fields.Char(string='Col-6')
    col_7 = fields.Char(string='Col-7')
    col_8 = fields.Char(string='Col-8')
    col_9 = fields.Char(string='Col-9')
    col_10 = fields.Char(string='Col-10')

    fabricator_name = fields.Char(string='Fabricator Name')
    location = fields.Char(string='Location')
    total_machines = fields.Integer(string='Total Machines')
    heavy_machines = fields.Integer(string='Heavy Machines')
    garment_design = fields.Text(string='Garment Design')
    plan_date = fields.Date(string='Plan Date')
    no_of_person = fields.Integer(string='No of Person')
    no_of_qc_person = fields.Integer(string='No of Person by QC')
    no_of_style = fields.Integer(string='No of Style')
    total_qty = fields.Float(string='Total Qty')
    status_by_qc = fields.Char(string='Status by QC')
    status_date = fields.Date(string='Status Date')
    next_week_remark = fields.Char(string='Remark')
    required_qty_vendor = fields.Char(string='Required Qty Vendor')
    next_week_plan = fields.Char(string='Next Week Planning')
    next_week_qty = fields.Float(string='Next Week Qty')

    # Additional columns you mentioned
    short_no = fields.Char(string='Fabric Short No')
    fabric_qty = fields.Float(string='Fabric Qty')
    purchase_order_no = fields.Char(string='Purchase Order No')
    sample = fields.Char(string='Sample')
    labtest = fields.Char(string='Labtest')
    pps = fields.Char(string='PPS')

    col_11 = fields.Char(string='Col-11')
    col_12 = fields.Char(string='Col-12')
    col_13 = fields.Char(string='Col-13')
    col_14 = fields.Char(string='Col-14')

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        report_id = self.env['api.report.configration'].search(
            [('report_type', '=', 'production_planning'), ('user_id', '=', self.env.user.id)], limit=1)
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
        test_list = tuple(test_list)
        key = key + (
            test_list,
        )
        return key

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "list":
            report_id = self.env['api.report.configration'].search(
                [('report_type', '=', 'production_planning'), ('user_id', '=', self.env.user.id)], limit=1)
            for field in report_id.line_ids.filtered(lambda l: l.is_readonly or l.is_invisible):
                for field_node in arch.xpath(f"//field[@name='{field.field_id.name}']"):
                    if field.is_readonly:
                        field_node.set("readonly", "1")
                    if field.is_invisible:
                        field_node.set("column_invisible", "1")
        return arch, view
