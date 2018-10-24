# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")


class HospitalNotes(models.Model):
    _name = "hos.notes"
    _rec_name = "person_id"

    current_time = fields.Datetime(string="Date", default=CURRENT_TIME)
    reminder = fields.Boolean(string="Reminder")
    reminder_time = fields.Datetime(string="Date", default=CURRENT_TIME)
    person_id = fields.Many2one(comodel_name="hos.person",
                                string="Name",
                                default=lambda self: self.env.user.person_id.id,
                                required=True)
    message = fields.Text(string="Message", required=True)
    attachment_detail = fields.Many2many(comodel_name="ir.attachment", string="Attachment")
