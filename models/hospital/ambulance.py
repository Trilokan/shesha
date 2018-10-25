# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

JOURNEY_TYPE = [("admission", "Admission"), ("discharge", "Discharge"), ("hospital_transfer", "Hospital Transfer")]
PROGRESS = [("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done"), ("cancel", "Cancel")]


class Ambulance(models.Model):
    _name = "hos.ambulance"
    _inherit = "mail.thread"

    name = fields.Char(sring="Name", readonly=True)
    date = fields.Date(string="Date", required=True, default=CURRENT_DATE)
    patient_id = fields.Many2one(comodel_name="hos.person", string="Patient", required=True)
    driver_id = fields.Many2one(comodel_name="hos.person", string="Driver", required=True)
    employee_ids = fields.Many2many(comodel_name="hos.person", string="Employee")
    progress = fields.Selection(selection=PROGRESS, string="Progress", default="draft")
    journey_type = fields.Selection(selection=JOURNEY_TYPE, string="Journey Type", default="admission")
    from_time = fields.Datetime(string="From Time", default=CURRENT_TIME)
    till_time = fields.Datetime(string="Till Time", default=CURRENT_TIME)
    from_location = fields.Text(string="From Location")
    till_location = fields.Text(string="Till Location")
    landmark = fields.Text(string="Landmark")
    duration = fields.Float(string="Duration", default=0)
    distance = fields.Float(string="Distance", default=0)
    amount = fields.Float(string="Amount", default=0)
    invoice_id = fields.Many2one(comodel_name="hos.invoice", string="Invoice")
    comment = fields.Text(string="Comment")
    writter = fields.Text(string="Writter", track_visibility='always')

    @api.multi
    def trigger_cancel(self):
        if not self.comment:
            raise exceptions.ValidationError("Error! Comment need before cancel")

        writter = "Ambulance Confirmation Processed by {0}".format(self.env.user.name)
        self.write({"progress": "cancel", "writter": writter})

    @api.multi
    def trigger_confirm(self):
        writter = "Ambulance Confirmation Processed by {0}".format(self.env.user.name)
        self.write({"progress": "confirmed", "writter": writter})

    @api.multi
    def trigger_done(self):
        if (self.duration <= 0) or (self.distance <= 0) or (self.unit_price <= 0):
            raise exceptions.ValidationError("Error! Please check Duration/ Distance/ rate Per KM")

        # Raise Invoice
        invoice_id = self.generate_invoice()

        writter = "Journey completed Processed by {0}".format(self.env.user.name)
        self.write({"progress": "done", "writter": writter})

    @api.multi
    def generate_invoice(self):
        pass
