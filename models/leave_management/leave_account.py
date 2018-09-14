# -*- coding: utf-8 -*-

from odoo import models, fields


# Account
class LeaveAccount(models.Model):
    _name = "leave.account"

    name = fields.Char(string="Account", required=True)
    code = fields.Char(string="Code", readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

