# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]
VOUCHER_TYPE = [("customer_payment", "Customer Payment"), ("vendor_payment", "Vendor Payment")]
PAYMENT_TYPE = [("cheque", "Cheque"), ("cash", "Cash"), ("rtgs", "RTGS")]


class Voucher(models.Model):
    _name = "hos.voucher"

    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    person_id = fields.Many2one(comodel_name="hos.person", string="Person")
    voucher_type = fields.Selection(selection=VOUCHER_TYPE, string="Type")
    payment_type = fields.Selection(selection=PAYMENT_TYPE, string="Payment Type")
    amount = fields.Float(string="Amount")
    credit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="credit_id", string="Credit")
    debit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="debit_id", string="Debit")
    balance = fields.Float(string="Balance")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress")

    # Bank Reference
    bank_id = fields.Many2one(comodel_name="Bank")
    reference = fields.Char(string="Reference")
    cheque_no = fields.Char(dtring="Cheque No")
    comment = fields.Text(string="Comment")

    def get_dr_lines(self, account_id):
        recs = self.env["journal.items"].search([("account_id", "=", account_id),
                                                 ("debit", ">", 0),
                                                 ("reconcile_id", "=", False)])

        res_dr = []

        for rec in recs:
            data = {"date": rec.date,
                    "name": rec.name,
                    "description": rec.description,
                    "debit_id": self.id,
                    "amount": rec.debit}
            res_dr.append(data)

        return res_dr

    def get_cr_lines(self, account_id):
        recs = self.env["journal.items"].search([("account_id", "=", account_id),
                                                 ("credit", ">", 0),
                                                 ("reconcile_id", "=", False)])

        res_cr = []

        for rec in recs:
            data = {"date": rec.date,
                    "name": rec.name,
                    "description": rec.description,
                    "credit_id": self.id,
                    "amount": rec.credit}
            res_cr.append(data)

        return res_cr

    @api.onchange("person_id")
    def onchange_person_id(self):
        self.credit_lines.unlink()
        self.debit_lines.unlink()

        if self.person_id:
            account_id = self.person_id.payable_id.id

            self.credit_lines = self.get_cr_lines(account_id)
            self.debit_lines = self.get_dr_lines(account_id)

    def reset_lines(self):
        for rec in self.credit_lines:
            rec.reconcile = 0

        for rec in self.debit_lines:
            rec.reconcile = 0

    def payment_tally(self, credits, payment):
        for credit in credits:
            diff = credit.amount - credit.reconcile
            if (diff > 0) and (payment > 0):
                if diff >= payment:
                    credit.reconcile = credit.reconcile + payment
                    payment = 0

                elif diff < payment:
                    credit.reconcile = credit.reconcile + diff
                    payment = payment - diff

        return payment

    @api.multi
    def trigger_customer_payment(self):
        self.reset_lines()

        credits = self.credit_lines
        debits = self.debit_lines

        payment = self.payment_tally(credits, self.amount)

        for debit in debits:
            payment = self.payment_tally(credits, debit.amount)
            debit.reconcile = debit.amount - payment
            debit.balance = payment

        self.balance = payment



    @api.multi
    def trigger_vendor_payment(self):
        self.reset_lines()

        credits = self.credit_lines
        debits = self.debit_lines

        payment = self.payment_tally(debits, self.amount)

        for credit in credits:
            payment = self.payment_tally(debits, credit.amount)
            credit.reconcile = credit.amount - payment
            credit.balance = payment

        self.balance = payment

    def gt(self):
        credits = self.env["voucher.line"].search([("credit_id", "=", self.id),
                                                   ("reconcile", ">", 0)])

        for rec in credits:
            pass


    @api.multi
    def trigger_confirm(self):

        debits = self.env["voucher.line"].search([("debit_id", "=", self.id),
                                                  ("reconcile", ">", 0)])


