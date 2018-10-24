# -*- coding: utf-8 -*-

from odoo import models, fields, api

PROGRESS = [("draft", "Draft"), ("Prescribed", "Prescribed")]


class Prescription(models.Model):
    _name = "patient.prescription"

    date = fields.Date(string="Date")
    patient_id = fields.Many2one(comodel_name="hos.person", string="Patient")
    treatment_id = fields.Many2one(comodel_name="hos.treatment", string="Patient")
    days = fields.Integer(string="Days")
    progress = fields.Selection(selection=PROGRESS, sring="Progress", default="draft")
    medicine_detail = fields.One2many(comodel_name="prescription.detail",
                                      inverse_name="prescription_id",
                                      string="Prescription")


