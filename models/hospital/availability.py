# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancel", "Cancel")]


# Hospital Availability
class HospitalAvailability(models.Model):
    _name = "hos.availability"
    _inherit = "mail.thread"
    _rec_name = "employee_id"

    employee_id = fields.Many2one(comodel_name="hos.person",
                                  string="Employee",
                                  default=lambda self: self.env.user.person_id.id,
                                  required=True)
    from_time = fields.Datetime(string="From Time", default=CURRENT_TIME, required=True)
    till_time = fields.Datetime(string="Till Time", default=CURRENT_TIME, required=True)
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.comoany_id.id)

    @api.multi
    def trigger_confirm(self):
        writter = "Availability Confirm By {0} on {1}".format(self.env.user.name, CURRENT_TIME)
        self.write({"progress": "confirmed", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        writter = "Availability Cancel By {0} on {1}".format(self.env.user.name, CURRENT_TIME)
        self.write({"progress": "cancel", "writter": writter})
