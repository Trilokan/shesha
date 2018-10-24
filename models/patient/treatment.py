# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")


class Treatment(models.Model):
    _name = "hos.treatment"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", required=True, default=CURRENT_DATE)
    patient_id = fields.Many2one(comodel_name="hos.person", string="Patient", required=True)
    symptoms_detail = fields.Many2many(comodel_name="patient.symptoms", string="Symptoms")
    diagnosis_detail = fields.Many2many(comodel_name="patient.diagnosis", string="Diagnosis")
    prescription_suggestion_detail = fields.Many2many(comodel_name="hos.product", string="Medicine Suggestion")
    prescription_detail = fields.One2many(comodel_name="patient.prescription",
                                          inverse_name="treatment_id",
                                          string="Prescription")
    # treatment_detail = fields.One2many(comodel_name="patient.treatment",
    #                                    inverse_name="treatment_id",
    #                                    string="Treatment")
    visit_detail = fields.One2many(comodel_name="patient.visit",
                                   inverse_name="treatment_id",
                                   string="Doctor Visit")
    bed_shift_detail = fields.One2many(comodel_name="bed.shifting",
                                       inverse_name="treatment_id",
                                       string="Bed Shifting")
    # reminder_detail = fields.One2many(comodel_name="hos.reminder",
    #                                   inverse_name="treatment_id",
    #                                   string="Reminder")
    # payment_detail = fields.One2many(comodel_name="hos.voucher",
    #                                  inverse_name="treatment_id",
    #                                  string="Payment")



