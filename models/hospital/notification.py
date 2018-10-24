# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS = [("draft", "Draft"), ("notified", "Notified")]


class Notification(models.Model):
    _name = "hos.notification"

    notify_time = fields.Datetime(string="Time", default=CURRENT_TIME, required=True)
    sender_id = fields.Many2one(comodel_name="hos.person", string="Sender", required=True)
    receiver_id = fields.Many2one(comodel_name="hos.person", string="Receiver", required=True)
    message = fields.Text(string="Message", required=True)
    attachment_detail = fields.Many2many(comodel_name="ir.attachment", string="Attachment")
    progress = fields.Selection(selection=PROGRESS, string="Progress", default="draft")
