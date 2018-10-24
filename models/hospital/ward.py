# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Ward(models.Model):
    _name = "hos.ward"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    bed_detail = fields.One2many(comodel_name="hos.bed", inverse_name="ward_id", string="Bed")
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    incharge_id = fields.Many2one(comodel_name="hos.person", string="Incharge")


