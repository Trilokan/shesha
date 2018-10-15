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
    amount = fields.Float(string="Amount")
    reconcile = fields.Float(string="Reconcile")
    balance = fields.Float(string="Balance")
    status = fields.Boolean(string="Status", default=False)
    credit_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")
    debit_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")
    current_id = fields.Many2one(comodel_name="hos.voucher", string="Voucher")
    sequence = fields.Integer(string="Sequence", default=10)

    item_id = fields.Many2one(comodel_name="journal.items", string="Journal Items")
    invoice_id = fields.Many2one(comodel_name="hos.invoice", string="Invoice")

    @api.model
    def create(self, vals):

        if "amount" in vals:
            if vals["amount"]:
                return super(VoucherLine, self).create(vals)
