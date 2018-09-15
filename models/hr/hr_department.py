# -*- coding: utf-8 -*-

from odoo import models, fields


# Department
class HRDepartment(models.Model):
    _name = "hr.department"

    name = fields.Char(string="Department", required=True)
    head_id = fields.Many2one(comodel_name="hr.employee", string="Department Head")
    member_ids = fields.Many2many(comodel_name="hr.employee", string="Department Members")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
