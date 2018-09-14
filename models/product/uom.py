# -*- coding: utf-8 -*-

from odoo import models, fields


# Product UOM
class UOM(models.Model):
    _name = "product.uom"
    _rec_name = "code"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_code', 'unique (code)', 'Error! UOM Code must be unique'),
                        ('unique_name', 'unique (name)', 'Error! UOM must be unique')]
