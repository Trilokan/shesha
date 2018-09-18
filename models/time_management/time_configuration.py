# -*- coding: utf-8 -*-

from odoo import fields, models


# Time Configuration
class TimeConfiguration(models.Model):
    _name = "time.configuration"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    value = fields.Float(string="Value", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

