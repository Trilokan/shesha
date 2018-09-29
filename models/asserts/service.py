# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [('draft', 'Draft'), ('confirmed', 'Confirmed')]


# Assert Service
class AssertsService(models.Model):
    _name = "asserts.service"
    _inherit = "mail.thread"
    _rec_name = "assert_id"

    date = fields.Date(string="Date", default=CURRENT_DATE, required=True)
    assert_id = fields.Many2one(comodel_name="hos.asserts", string="Assert", required=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Service", required=True)
    description = fields.Text(string="Description", required=True)
    attachment = fields.Many2many(comodel_name="ir.attachment", string="Attachment")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")

    @api.multi
    def trigger_confirm(self):
        msg = "Asserts Service by {0} on {1}"
        writter = msg.format(self.env.user.name, CURRENT_TIME)

        self.write({"progress": "confirmed", "writter": writter})

    @api.model
    def create(self, vals):
        msg = "Assert Service Created by {0} on {1}"
        vals["writter"] = msg.format(self.env.user.name, CURRENT_TIME)
        return super(AssertsService, self).create(vals)
