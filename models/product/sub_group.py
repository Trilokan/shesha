# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Product Sub Group
class ProductSubGroup(models.Model):
    _name = "product.sub.group"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    group_id = fields.Many2one(comodel_name="product.group", string="Group", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_code', 'unique (code)', 'Error! Sub-Group Code must be unique'),
                        ('unique_name', 'unique (name)', 'Error! Sub-Group must be unique')]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "[{0}] {1}".format(record.code, record.name)
            result.append((record.id, name))
        return result
