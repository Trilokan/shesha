# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions


# Salary Rule Type
class SalaryRuleCode(models.Model):
    _name = "salary.rule.code"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
