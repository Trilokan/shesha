# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class HospitalNotes(models.Model):
    _name = "hos.notes"
    _rec_name = "person_id"

    date = fields.Date(string="Date", default=CURRENT_DATE, required=True)
    reminder = fields.Boolean(string="Set Reminder")
    time = fields.Float(string="Time")
    person_id = fields.Many2one(comodel_name="hos.person",
                                string="Name",
                                default=lambda self: self.env.user.person_id.id,
                                required=True)
    message = fields.Text(string="Message", required=True)
    attachment_detail = fields.Many2many(comodel_name="ir.attachment", string="Attachment")

