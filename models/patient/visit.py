# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Visit(models.Model):
    _name = "patient.visit"

    treatment_id = fields.Many2one(comodel_name="hos.treatment", string="Patient", required=True)
    date = fields.Datetime(string="Date", required=True)
    employee_id = fields.Many2one(comodel_name="hos.person", string="Doctor", required=True)
    description = fields.Text(string="Visit Detail")
    comment = fields.Text(string="Comment")

