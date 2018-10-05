# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [("draft", "Draft"), ("posted", "Posted")]


class JournalItems(models.Model):
    _name = "journal.items"

    entry_id = fields.Many2one(comodel_name="journal.entries", string="Journal Entries")
    date = fields.Date(string="Date", default=CURRENT_DATE)
    name = fields.Char(string="Name", readonly=True)
    period_id = fields.Many2one(comodel_name="period.period",
                                string="Period",
                                default=lambda self: self.env.context.get("period_id", False),
                                required=True)
    journal_id = fields.Many2one(comodel_name="hos.journal",
                                 string="Journal",
                                 default=lambda self: self.env.context.get("journal_id", False))
    reference = fields.Text(string="Reference")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")

    invoice_id = fields.Many2one(comodel_name="hos.invoice", string="Invoice")
    account_id = fields.Many2one(comodel_name="hos.account", string="Account")
    description = fields.Text(string="Description")
    credit = fields.Float(string="Credit", default=0)
    debit = fields.Float(string="Credit", default=0)
    reconcile_id = fields.Many2one(comodel_name="hos.reconcile", string="Reconcile")

    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super(JournalItems, self).create(vals)
