# -*- coding: utf-8 -*-

from odoo import models, fields


# Product Location
class HospitalLocation(models.Model):
    _name = "product.location"
    _rec_name = "code"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", compute="_get_code")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    location_left = fields.Integer(string="Parent Left", required=True)
    location_right = fields.Integer(string="Parent Right", required=True)

    _sql_constraints = [('unique_name', 'unique (name)', 'Error! Product Location must be unique')]

    def _get_code(self):
        for record in self:
            recs = self.env["product.location"].search([("location_left", "<=", record.location_left),
                                                        ("location_right", ">=", record.location_right)])

            recs = recs.sorted(key=lambda r: r.location_left)
            record.code = "/".join(str(x.name) for x in recs)
