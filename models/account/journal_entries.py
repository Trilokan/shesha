# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [("draft", "Draft"), ("posted", "Posted")]


class JournalEntries(models.Model):
    _name = "journal.entries"
    _rec_name = "name"

    date = fields.Date(string="Date", default=CURRENT_DATE)
    name = fields.Char(string="Name", readonly=True)
    period_id = fields.Many2one(comodel_name="period.period", string="Period", required=True)
    journal_id = fields.Many2one(comodel_name="hos.journal", string="Journal")
    reference = fields.Char(string="Reference")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    journal_item = fields.One2many(comodel_name="journal.items", inverse_name="entry_id", string="Journal Item")

    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super(JournalEntries, self).create(vals)
