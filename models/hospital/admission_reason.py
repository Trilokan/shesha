# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AdmissionReason(models.Model):
    _name = "admission.reason"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id)


