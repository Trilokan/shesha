# -*- coding: utf-8 -*-

from odoo import models, fields, api

PRESCRIPTION_TYPE = [("after_food", "After Food"), ("before_food", "Before Food")]


class PrescriptionDetail(models.Model):
    _name = "prescription.detail"

    product_id = fields.Many2one(comodel_name="hos.product", string="Medicine")
    quantity = fields.Float(string="Quantity")
    morning = fields.Boolean(string="Morning")
    noon = fields.Boolean(string="Noon")
    night = fields.Boolean(string="Evening")
    prescription_type = fields.Selection(selection=PRESCRIPTION_TYPE, string="Type")
    prescription_id = fields.Many2one(comodel_name="patient.prescription", string="Prescription")

