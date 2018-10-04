# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]


class JournalEntries(models.Model):
    _name = "journal.entries"

    date = fields.Date(string="Date", default=CURRENT_DATE)
    name = fields.Char(string="Name", readonly=True)
    period_id = fields.Many2one(comodel_name="period.period", string="Period", required=True)
    journal_id = fields.Many2one(comodel_name="hos.journal", string="Journal")
    reference = fields.Text(string="Reference")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress")
    journal_item = fields.One2many(comodel_name="journal.item", string="Journal Item")

    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
