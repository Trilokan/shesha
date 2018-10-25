# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

PROGRESS = [("draft", "Draft"), ("notified", "Notified")]


class Notification(models.Model):
    _name = "hos.notification"
    _inherit = "mail.thread"

    date = fields.Datetime(string="Date", default=CURRENT_TIME, required=True)
    sender_id = fields.Many2one(comodel_name="hos.person", string="Sender", required=True,
                                default=lambda self: self.env.user.person_id.id)
    receiver_id = fields.Many2one(comodel_name="hos.person", string="Receiver", required=True)
    message = fields.Text(string="Message", required=True)
    attachment_detail = fields.Many2many(comodel_name="ir.attachment", string="Attachment")
    progress = fields.Selection(selection=PROGRESS, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    @api.multi
    def trigger_notification(self):
        writter = "{0} message is notified to {1} on {2}".format(self.sender_id.name,
                                                                 self.receiver_id.name,
                                                                 CURRENT_TIME)
        self.write({"progress": "notified",
                    "writter": writter})
