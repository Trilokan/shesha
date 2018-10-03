# -*- coding: utf-8 -*-

from odoo import models, fields


# Store Configuration
class StoreConfiguration(models.Model):
    _name = "store.conf"

    err_01 = fields.Boolean(string="Check Stock on Purchase", help="Excess Purchase limit")
    err_02 = fields.Boolean(string="Check Stock on Sales", help="Negative Stock Acceptation")

    # Virtual Location
    location_purchase_id = fields.Many2one(comodel_name="product.location", string="Virtual Purchase Location")
    location_sale_id = fields.Many2one(comodel_name="product.location", string="Virtual Sale Location")

    # Physical Location
    location_store_id = fields.Many2one(comodel_name="product.location", string="Store Location")
    location_pharmacy_id = fields.Many2one(comodel_name="product.location", string="Pharmacy Location")

    # Other Location
    location_assert_id = fields.Many2one(comodel_name="product.location", string="Assert Location")
    location_loss_id = fields.Many2one(comodel_name="product.location", string="Inventory Loss Location")
    location_block_id = fields.Many2one(comodel_name="product.location", string="Block list Location")

    # Location
    location_left = fields.Integer(string="Location Left")
    location_right = fields.Integer(string="Location Right")

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 required=True)

    _sql_constraints = [('company_uniq', 'unique (company_id)', 'The company name must be unique !')]

