# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]


class VoucherLine(models.Model):
    _name = "voucher.line"

    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    amount = fields.Float(string="Amount")
    reconcile = fields.Float(string="Reconcile")
    balance = fields.Float(string="Balance")
    credit_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")
    debit_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")

