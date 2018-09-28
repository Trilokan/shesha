# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]


class JournalItem(models.Model):
    _name = "journal.item"

    date = fields.Date(string="Date", default=datetime.now().strftime("%Y-%m-%d"))
    name = fields.Char(string="Name")
    invoice_id = fields.Many2one(comodel_name="hos.invoice", string="Invoice")
    account_id = fields.Many2one(comodel_name="hos.account", string="Account")
    description = fields.Text(string="Description")
    credit = fields.Float(string="Credit")
    debit = fields.Float(string="Credit")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress")
    reconcile_id = fields.Many2one(comodel_name="hos.reconcile", string="Reconcile")
    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)







