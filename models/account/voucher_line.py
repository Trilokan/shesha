# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]


class VoucherLine(models.Model):
    _name = "voucher.line"
    _order = "sequence"

    date = fields.Date(string="Date", default=CURRENT_DATE)
    description = fields.Text(string="Description")
    amount = fields.Float(string="Amount", default=0)
    reconcile = fields.Float(string="Reconcile", default=0)
    balance = fields.Float(string="Balance", default=0)
    credit_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")
    debit_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")
    current = fields.Boolean(string="Current")
    sequence = fields.Integer(string="Sequence", default=10)

    item_id = fields.Many2one(comodel_name="journal.items", string="Journal Items")
    invoice_id = fields.Many2one(comodel_name="hos.invoice", string="Invoice")

    @api.model
    def create(self, vals):

        if "amount" in vals:
            if vals["amount"]:
                return super(VoucherLine, self).create(vals)
