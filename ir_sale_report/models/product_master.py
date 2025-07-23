from odoo import models, fields

class SeasonMaster(models.Model):
    _name = "season.master"

    name = fields.Char(string="Name")

class ColorMaster(models.Model):
    _name = "color.master"

    name = fields.Char(string="Name")

class SizeMaster(models.Model):
    _name = "size.master"

    name = fields.Char(string="Name")

class RatioMaster(models.Model):
    _name = "ratio.master"

    name = fields.Char(string="Name")

class DesignMaster(models.Model):
    _name = "design.master"

    name = fields.Char(string="Name")

class EmbroideryMaster(models.Model):
    _name = "embroidery.master"

    name = fields.Char(string="Name")

class BrandMaster(models.Model):
    _name = "brand.master"

    name = fields.Char(string="Name")

class FitMeasurement(models.Model):
    _name = "fit.measurement"

    name = fields.Char(string="Name")

class WashingItem(models.Model):
    _name = "washing.item"

    name = fields.Char(string="Name")

class ProductDesignType(models.Model):
    _name = "product.design.type"

    name = fields.Char(string="Name")