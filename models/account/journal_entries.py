# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]


class JournalEntries(models.Model):
    _name = "journal.entries"

    date = fields.Date(string="Date", default=datetime.now().strftime("%Y-%m-%d"))
    name = fields.Char(string="Name")
    period_id = fields.Many2one(comodel_name="period.period", string="Period")
    journal_id = fields.Many2one(comodel_name="", string="Journal")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress")
    journal_item = fields.One2many(comodel_name="journal.item", string="Journal Item")
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
