# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

ADMISSION_STATUS = [("emergency", "Emergency"), ("normal", "Normal")]
ADMISSION_PROGRESS = [("draft", "Draft"), ("admitted", "Admitted"), ("cancel", "Cancel")]
DISCHARGE_STATUS = [("emergency", "Emergency"), ("normal", "Normal")]
DISCHARGE_PROGRESS = [("admitted", "Admitted"), ("discharged", "Discharged")]


class AdmissionDischarge(models.Model):
    _name = "admission.discharge"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", required=True, default=CURRENT_DATE)
    patient_id = fields.Many2one(comodel_name="hos.person", string="Patient", required=True)
    mobile = fields.Char(string="Mobile", required=True)
    alternate_mobile = fields.Char(string="Alternate Mobile")
    email = fields.Char(string="email")

    # Admission Details
    admission_on = fields.Date(string="Admission On", default=CURRENT_DATE)
    admission_by = fields.Many2one(comodel_name="hos.person", string="Admission By")
    admission_reason = fields.Many2one(comodel_name="admission.reason", string="Admission Reason")
    admission_status = fields.Selection(selection=ADMISSION_STATUS, string="Admission Status")
    admission_progress = fields.Selection(selection=ADMISSION_PROGRESS, string="Admission Progress", default="draft")
    admission_comment = fields.Text(string="Admission Comment")
    admission_attachment = fields.Many2many(comodel_name="ir.attachment", string="Attachment")

    treatment_id = fields.Many2one(comodel_name="hos.treatment", string="Treatment")
    # payment_detail = ""

    # Discharge Details
    discharge_on = fields.Date(string="Discharge On")
    discharge_by = fields.Many2one(comodel_name="hos.person", string="Discharge By")
    discharge_reason = fields.Many2one(comodel_name="admission.reason", string="Admission Reason")
    discharge_status = fields.Selection(selection=DISCHARGE_STATUS, string="Discharge Status")
    discharge_progress = fields.Selection(selection=DISCHARGE_PROGRESS, string="Discharge Progress", default="draft")
    discharge_comment = fields.Text(string="Discharge Comment")
    discharge_attachment = fields.Many2many(comodel_name="ir.attachment", string="Attachment")

    # Approval
    account_approval = fields.Boolean(string="Account Approval")
    doctor_approval = fields.Boolean(string="Doctor Approval")

    writter = fields.Char(string="Writter", track_visibility="always")
    company_id = fields.Many2one(comodel_name="res.company", default=lambda self: self.env.user.company_id.id)

    @api.multi
    def trigger_admit(self):
        writter = "Admission processed by {0}".format(self.env.user.name)
        self.write({"admission_progress": "admitted",
                    "discharge_progress": "admitted",
                    "writter": writter})

    @api.multi
    def trigger_discharge(self):
        if (not self.account_approval) or (not self.doctor_approval):
            raise exceptions.ValidationError("Error! Please check Doctor/ Account Approval..")

        writter = "Discharge processed by {0}".format(self.env.user.name)
        self.write({"discharge_progress": "admitted", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        if not self.admission_comment:
            raise exceptions.ValidationError("Error! Comment Need before cancellation")

        writter = "Admission Cancellation  processed by {0}".format(self.env.user.name)
        self.write({"discharge_progress": "cancel", "writter": writter})

    # Smart Button
    @api.multi
    def smart_view_patient(self):
        view = self.env.ref('shesha.view_hos_person_form')

        return {
            'name': 'Patient',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'hos.person',
            'type': 'ir.actions.act_window',
            'res_id': self.patient_id.id,
            'context': self.env.context
        }

    @api.multi
    def smart_view_status(self):
        pass

    @api.multi
    def smart_view_payment(self):
        pass

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return (AdmissionDischarge, self).create(vals)
