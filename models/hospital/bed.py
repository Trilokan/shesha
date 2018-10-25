# -*- coding: utf-8 -*-

from odoo import models, fields


class Bed(models.Model):
    _name = "hos.bed"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    ward_id = fields.Many2one(comodel_name="hos.ward", string="Ward")
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id)


