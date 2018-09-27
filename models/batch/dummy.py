# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Dummy Batch
class DummyBatch(models.Model):
    _name = "dum.batch"

    batch_no = fields.Char(string="Batch", required=True)
    manufactured_date = fields.Date(string="Manufacturing Date", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True)
    mrp_rate = fields.Float(string="MRP", default=0)
    unit_price = fields.Float(string="Unit Price", default=0)
    quantity = fields.Float(string="Quantity", required=True)
    move_id = fields.Many2one(comodel_name="hos.move", string="Move", required=True)

    def generate_batch(self, vals):
        move_id = self.env["hos.move"].search([("id", "=", vals["move_id"])])
        batch = self.env["hos.batch"].search([("batch_no", "=", vals["batch_no"]),
                                              ("product_id", "=", move_id.product_id.id)])

        vals["product_id"] = move_id.product_id.id
        if not batch:
            self.env["hos.batch"].create(vals)

    @api.model
    def create(self, vals):
        self.generate_batch(vals)

        return super(DummyBatch, self).create(vals)
