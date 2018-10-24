# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancel", "Cancel")]


# Schedule
class HospitalSchedule(models.Model):
    _name = "hos.schedule"
    _inherit = "mail.thread"

    person_id = fields.Many2one(comodel_name="hos.person", string="Scheduler", required=True)
    patient_id = fields.Many2one(comodel_name="hos.person", string="Patient")
    schedule_time = fields.Datetime(string="Time", required=True)
    schedule_type_id = fields.Many2one(comodel_name="schedule.type", string="Schedule Type")
    reason = fields.Many2one(comodel_name="schedule.reason", string="Reason")
    reference = fields.Char(string="Reference")

    writter = fields.Text(string="Writter")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    comment = fields.Text(string="Comment")

