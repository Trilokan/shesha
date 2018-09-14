# -*- coding: utf-8 -*-

from odoo import models, fields


# Tax
class Tax(models.Model):
    _name = "product.tax"
    _rec_name = "code"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    rate = fields.Float(string="Rate", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_code', 'unique (code)', 'Error! Tax Code must be unique'),
                        ('unique_code', 'unique (rate)', 'Error! Tax Rate must be unique')]
