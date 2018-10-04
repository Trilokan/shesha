# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]
VOUCHER_TYPE = [("customer_payment", "Customer Payment"), ("vendor_payment", "Vendor Payment")]
PAYMENT_TYPE = [("cheque", "Cheque"), ("cash", "Cash"), ("rtgs", "RTGS")]


class Voucher(models.Model):
    _name = "hos.voucher"

    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    journal_id = fields.Many2one(comodel_name="hos.journal")
    voucher_type = fields.Selection(selection=VOUCHER_TYPE, string="Type")
    payment_type = fields.Selection(selection=PAYMENT_TYPE, string="Payment Type")
    amount = fields.Float(string="Amount")
    credit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="credit_id", string="Credit")
    debit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="debit_id", string="Debit")
    balance = fields.Float(string="Balance")

    # Bank Reference
    bank_id = fields.Many2one(comodel_name="Bank")
    reference = fields.Char(string="Reference")
    cheque_no = fields.Char(dtring="Cheque No")
    comment = fields.Text(string="Comment")


class VoucherLine(models.Model):
    _name = ""

    date = ""
    name = ""
    description = ""
    credit = ""
    debit = ""



