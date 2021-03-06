# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime
from .. import reconciliation as rex

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [("draft", "Draft"), ("posted", "Posted")]
VOUCHER_TYPE = [("customer_payment", "Customer Payment"), ("vendor_payment", "Vendor Payment")]
PAYMENT_TYPE = [("cheque", "Cheque"), ("cash", "Cash"), ("rtgs", "RTGS")]


class Voucher(models.Model):
    _name = "hos.voucher"
    _rec_name = "name"
    _inherit = "mail.thread"

    date = fields.Date(string="Date", default=CURRENT_DATE)
    name = fields.Char(string="Name")
    person_id = fields.Many2one(comodel_name="hos.person", string="Person")
    voucher_type = fields.Selection(selection=VOUCHER_TYPE, string="Type")
    payment_type = fields.Selection(selection=PAYMENT_TYPE, string="Payment Type")
    amount = fields.Float(string="Amount", default=0)
    balance = fields.Float(string="Balance", default=0)
    credit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="credit_id", string="Credit")
    debit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="debit_id", string="Debit")
    current_lines = fields.One2many(comodel_name="voucher.line", inverse_name="current_id", string="Current")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(sring="Writter", track_visibility='always')

    # Bank Reference
    bank_id = fields.Many2one(comodel_name="Bank")
    reference = fields.Char(string="Reference")
    cheque_no = fields.Char(dtring="Cheque No")
    comment = fields.Text(string="Comment")

    def get_lines(self, recs):
        res = []

        for rec in recs:
            data = {"date": rec.date,
                    "description": rec.description,
                    "credit_id": self.id if rec.credit else False,
                    "debit_id": self.id if rec.debit else False,
                    "item_id": rec.id,
                    "account_id": rec.account_id.id,
                    "amount": rec.credit or rec.debit}
            res.append((0, 0, data))

        return res

    @api.onchange("person_id")
    def onchange_person_id(self):
        self.credit_lines.unlink()
        self.debit_lines.unlink()
        self.current_lines.unlink()

        if self.person_id:
            account_id = self.person_id.payable_id.id

            recs = self.env["journal.items"].search([("account_id", "=", account_id),
                                                     ("reconcile_id", "=", False),
                                                     ("credit", ">", 0)])

            self.credit_lines = self.get_lines(recs)

            recs = self.env["journal.items"].search([("account_id", "=", account_id),
                                                     ("reconcile_id", "=", False),
                                                     ("debit", ">", 0)])

            self.debit_lines = self.get_lines(recs)

    def amount_update(self):
        data = {"date": self.date,
                "description": "Payment",
                "sequence": 1,
                "current_id": self.id,
                "amount": self.amount}

        self.current_lines = [(0, 0, data)]

    def reset_current(self, obj):
        for rec in obj:
            rec.reconcile = 0
            rec.balance = 0

            if rec.current_id:
                rec.unlink()

    @api.multi
    def trigger_reconcile(self):
        self.reset_current(self.credit_lines)
        self.reset_current(self.debit_lines)
        self.reset_current(self.current_lines)
        self.amount_update()

        credit_lines, debit_lines = self.ghy(self.credit_lines, self.debit_lines, self.current_lines)

        self.env["hos.reconcile"].reconciliation(credit_lines, debit_lines)
        self.balance = self.current_lines.balance

        writter = "{0} Reconcile by {1} on {2}".format(self.payment_type.upper(), self.env.user.name, CURRENT_TIME)
        self.write({"writter": writter})

    def ghy(self, credit, debit, current):
        if self.voucher_type == "customer_payment":
            credit = current + credit
        elif self.voucher_type == "vendor_payment":
            debit = current + debit

        return credit, debit

    def compute_balance(self, obj):
        reconcile = 0
        for rec in obj:
            if rec.status:
                rec.balance = rec.amount - rec.reconcile
                reconcile = reconcile + rec.reconcile

        return reconcile

    @api.multi
    def trigger_check_balance(self):
        self.balance = self.current_lines.balance

        credit_reconcile = self.compute_balance(self.credit_lines)
        debit_reconcile = self.compute_balance(self.debit_lines)
        current_reconcile = self.compute_balance(self.current_lines)

        credit, debit = self.ghy(credit_reconcile, debit_reconcile, current_reconcile)

        if credit != debit:
            raise exceptions.ValidationError("Error! Please check reconciliation amount")

    def get_invoice_id(self, status, invoice_id):
        data_id = False
        if status == "reconcile":
            if invoice_id:
                data_id = invoice_id.id

        return data_id

    def trigger_journal_items(self, account_id, partner_account_id, reconcile_id, vals):
        journal_items = []

        credit_lines, debit_lines = self.ghy(self.credit_lines,
                                             self.debit_lines,
                                             self.current_lines)

        for rec in credit_lines:
            cr_amount_status = [("credit", "amount", rec.amount),
                                ("debit", "reconcile", rec.reconcile),
                                ("debit", "balance", rec.balance)]

            if rec.status:
                for line, status, amount in cr_amount_status:
                    data = {"invoice_id": self.get_invoice_id(status, rec),
                            "account_id": account_id.id if rec.current_id else partner_account_id.id,
                            "description": rec.description,
                            "credit": amount if line == "credit" else 0,
                            "debit": amount if line == "debit" else 0,
                            "reconcile_id": reconcile_id if status != "balance" else False}

                    data.update(vals)
                    journal_items.append((0, 0, data))

        return journal_items

    @api.multi
    def trigger_journal_entries(self):
        self.trigger_check_balance()

        account_id = self.env["account.account"].search([("na")])
        partner_account_id = self.env["account.account"].search([("")])
        reconcile_id = self.env["hos.reconcile"].create({})
        journal_id = self.env["hos.journal"].search([("name", "=", "Payment")])
        period_id = self.env["period.period"].search([("from_date", "<=", self.date), ("till_date", ">=", self.date)])

        vals = {"date": self.date,
                "period_id": period_id,
                "journal_id": journal_id,
                "reference": self.name,
                "progress": "posted"}

        journal_items = self.trigger_journal_items(account_id, partner_account_id, reconcile_id, vals)

        data = {"journal_item": journal_items}
        data.update(vals)

        self.env["journal.entries"].create(data)

        writter = "{0} Validated by {1} on {2}".format(self.payment_type.upper(), self.env.user.name, CURRENT_TIME)
        self.write({"progress": "posted", "writter": writter})

    @api.model
    def create(self, vals):
        code = "{0}{1}".format(self._name, vals["voucher_type"])
        vals["name"] = self.env["ir.sequence"].next_by_code(code)
        return super(Voucher, self).create(vals)





