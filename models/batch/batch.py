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
    store_quantity = fields.Float(string="Quantity", compute="_get_store_quantity")

    def _get_store_quantity(self):
        location = self.env.user.company_id.location_store_id.id

        for rec in self:
            rec.store_quantity = rec.get_batch_quantity(rec.id, location)

    def get_batch_quantity(self, batch_id, location):
        source = [("batch_id", "=", batch_id),
                  ("source_location_id", "=", location),
                  ("progress", "=", "moved")]

        destination = [("batch_id", "=", batch_id),
                       ("destination_location_id", "=", location),
                       ("progress", "=", "moved")]

        return self.env["hos.stock"].get_stock("batch.move", source, destination)

