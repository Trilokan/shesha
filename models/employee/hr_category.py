# -*- coding: utf-8 -*-

from odoo import models, fields


# Category
class HRCategory(models.Model):
    _name = "hr.category"

    name = fields.Char(string="Category", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
