# -*- coding: utf-8 -*-

from odoo import models, fields


# Batch
class Batch(models.Model):
    _name = "hos.batch"
    _rec_name = "batch_no"

    product_id = fields.Many2one(comodel_name="hos.product",
                                 string="Product",
                                 readonly=True)
    batch_detail = fields.One2many(comodel_name="batch.move",
                                   inverse_name="batch_id",
                                   string="Batch Detail")
    batch_no = fields.Char(string="Batch", readonly=True)
    manufactured_date = fields.Date(string="Manufacturing Date", readonly=True)
    expiry_date = fields.Date(string="Expiry Date", readonly=True)
    mrp_rate = fields.Float(string="MRP", default=0, readonly=True)
    unit_price = fields.Float(string="Unit Price", default=0, readonly=True)
    quantity = fields.Float(string="Quantity", readonly=True)
