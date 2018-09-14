# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Product Group
class ProductGroup(models.Model):
    _name = "product.group"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_code', 'unique (code)', 'Error! Group Code must be unique'),
                        ('unique_name', 'unique (name)', 'Error! Group must be unique')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "[{0}] {1}".format(record.code, record.name)
            result.append((record.id, name))
        return result
