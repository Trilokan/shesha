# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HospitalUsers(models.Model):
    _name = "res.users"
    _inherit = "res.users"

    location_id = fields.Many2one(comodel_name="product.location", string="Location")
    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="E-mail", readonly=True)
    contact_no = fields.Char(string="Contact No", readonly=True)
    alternate_contact = fields.Char(string="Alternate Contact", readonly=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Person", required=True)

    @api.model
    def create(self, vals):
        person_id = self.env["hos.person"].search([("id", "=", vals["person_id"])])

        vals["name"] = person_id.name
        vals["email"] = person_id.email
        vals["mobile"] = person_id.mobile

        person_id.write({"is_user": True})

        return super(HospitalUsers, self).create(vals)
