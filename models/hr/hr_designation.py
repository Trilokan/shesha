# -*- coding: utf-8 -*-

from odoo import models, fields


# Designation
class HRDesignation(models.Model):
    _name = "hr.designation"

    name = fields.Char(string="Designation", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

