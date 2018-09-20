# -*- coding: utf-8 -*-

from odoo import models, fields


# Warehouse
class HospitalWarehouse(models.Model):
    _name = "product.warehouse"
    _rec_name = "location_id"

    product_id = fields.Many2one(comodel_name="hos.product", string="Product", readonly=True)
    location_id = fields.Many2one(comodel_name="product.location", string="Location", readonly=True)
    quantity = fields.Float(string="Quantity", compute="_get_stock")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_product_location', 'unique (product_id, location_id)',
                         'Error! Product location must be unique')]

    def _get_stock(self):
        for record in self:
            source = [("product_id", "=", record.product_id.id),
                      ("source_location_id", "=", record.location_id.id),
                      ("progress", "=", "moved"),
                      ("batch_id", "=", False)]

            destination = [("product_id", "=", record.product_id.id),
                           ("destination_location_id", "=", record.location_id.id),
                           ("progress", "=", "moved"),
                           ("batch_id", "=", False)]

            record.quantity = self.env["hos.stock"].get_stock(source, destination)

    def generate_warehouse(self, product_id, location_id):
        warehouse = self.env["product.warehouse"].search([("product_id", "=", product_id),
                                                          ("location_id", "=", location_id)])

        if not warehouse:
            warehouse.create({"product_id": product_id,
                              "location_id": location_id})

