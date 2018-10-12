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
    credit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="credit_id", string="Credit")
    debit_lines = fields.One2many(comodel_name="voucher.line", inverse_name="debit_id", string="Debit")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(sring="Writter", track_visibility='always')

    # Bank Reference
    bank_id = fields.Many2one(comodel_name="Bank")
    reference = fields.Char(string="Reference")
    cheque_no = fields.Char(dtring="Cheque No")
    comment = fields.Text(string="Comment")

    def get_line_id(self, record_id, pay_type, self_type):
        result = False

        if pay_type == self_type:
            result = record_id

        return result

    def get_amount(self, rec, pay_type):
        result = 0

        if pay_type == "credit":
            result = rec.credit
        elif pay_type == "debit":
            result = rec.debit

        return result

    def get_lines(self, records, pay_type):
        res = []

        for record in records:
            data = {"date": record.date,
                    "description": record.description,
                    "credit_id": self.get_line_id(self.id, pay_type, "credit"),
                    "debit_id": self.get_line_id(self.id, pay_type, "debit"),
                    "item_id": record.id,
                    "amount": self.get_amount(record, pay_type)}
            res.append(data)

        return res

    @api.onchange("person_id")
    def onchange_person_id(self):
        self.credit_lines.unlink()
        self.debit_lines.unlink()

        if self.person_id:
            account_id = self.person_id.payable_id.id

            cr_records = self.env["journal.items"].search([("account_id", "=", account_id),
                                                           ("credit", ">", 0),
                                                           ("reconcile_id", "=", False)])

            dr_records = self.env["journal.items"].search([("account_id", "=", account_id),
                                                           ("debit", ">", 0),
                                                           ("reconcile_id", "=", False)])

            self.debit_lines = self.get_lines(dr_records, "debit")
            self.credit_lines = self.get_lines(cr_records, "credit")

    def amount_update(self):
        data = {"date": self.date,
                "description": "Payment",
                "sequence": 1,
                "current": True,
                "amount": self.amount}

        if self.voucher_type == "customer_payment":
            if self.amount:
                data["debit_id"] = self.id
                self.debit_lines = (0, 0, data)

        elif self.voucher_type == "vendor_payment":
            if self.amount:
                data["credit_id"] = self.id
                self.credit_lines = (0, 0, data)

    def reset_current(self, obj):
        for rec in obj:
            rec.reconcile = 0
            rec.balance = 0
            if rec.current:
                rec.unlink()

    def generate_balance(self, obj):
        for rec in obj:
            if rec.reconcile:
                balance = rec.amount - rec.reconcile
                if rec.balance != balance:
                    raise exceptions.ValidationError("Error! Please check reconcillation and balance amount")

    @api.multi
    def trigger_check_balance(self):
        self.generate_balance(self.credit_lines)
        self.generate_balance(self.debit_lines)

    @api.multi
    def trigger_reconcile(self):
        self.reset_current(self.credit_lines)
        self.reset_current(self.debit_lines)
        self.amount_update()

        for rec in self.credit_lines:

            rec.balance = self.reconcilation(self.debit_lines, rec.amount)
            rec.reconcile = rec.amount - rec.balance

        writter = "{0} Reconcile by {1} on {2}".format(self.payment_type.upper(), self.env.user.name, CURRENT_TIME)
        self.write({"writter": writter})

    def reconcilation(self, obj, value):
        for rec in obj:

            diff = rec.amount - rec.reconcile
            if diff > 0:
                if diff >= value:
                    rec.reconcile = rec.reconcile + value
                    value = 0

                elif diff < value:
                    rec.reconcile = rec.reconcile + diff
                    value = value - diff

            rec.balance = rec.amount - rec.reconcile

        return value

    def get_journal_id(self):
        journal_id = False
        if self.payment_type == "cash":
            obj = self.env["hos.journal"].search([("name", "=", "Cash")])
            journal_id = obj.id

        elif self.payment_type in ["cheque", "rtgs"]:
            obj = self.env["hos.journal"].search([("name", "=", "Bank")])
            journal_id = obj.id

        return journal_id

    def get_account_id(self):
        account_id = False
        if self.payment_type == "cash":
            obj = self.env["hos.account"].search([("name", "=", "Cash")])
            account_id = obj.id
        elif self.payment_type in ["cheque", "rtgs"]:
            obj = self.env["hos.account"].search([("name", "=", "Bank")])
            account_id = obj.id

        return account_id

    def get_partner_account_id(self):
        account_id = False
        if self.voucher_type == "customer_payment":
            account_id = self.person_id.payable_id.id
        elif self.voucher_type == "vendor_payment":
            account_id = self.person_id.receivable_id.id

        return account_id

    def generate_journal_items(self, invoice_id, journal_id, account_id, credit, debit, reconcile_id, period_id):

        data = {"date": self.date,
                "journal_id": journal_id,
                "period_id": period_id,
                "reference": self.name,
                "progress": "posted",
                "invoice_id": invoice_id,
                "account_id": account_id,
                "description": 0,
                "credit": credit,
                "debit": debit,
                "reconcile_id": reconcile_id}

        return data

    def trigger_journal_items(self, account_id, partner_account_id, reconcile_id, journal_id, period_id):

        journal_items = []

        for rec in self.credit_lines:
            if rec.reconcile:
                if rec.current:
                    vals = self.generate_journal_items(False, journal_id, account_id, 0, rec.amount, False, period_id)
                else:
                    vals = self.generate_journal_items(False, journal_id, partner_account_id, 0, rec.amount, reconcile_id, period_id)
                journal_items.append((0, 0, vals))
                vals = self.generate_journal_items(False, journal_id, partner_account_id, rec.reconcile, 0, reconcile_id, period_id)
                journal_items.append((0, 0, vals))
                vals = self.generate_journal_items(False, journal_id, partner_account_id, rec.balance, 0, False, period_id)
                journal_items.append((0, 0, vals))

                rec.item_id.write({"reconcile_id": reconcile_id})

        for rec in self.debit_lines:
            if rec.reconcile:
                if rec.current:
                    vals = self.generate_journal_items(False, journal_id, account_id, rec.amount, 0, False, period_id)
                else:
                    vals = self.generate_journal_items(False, journal_id, partner_account_id, rec.amount, 0, reconcile_id, period_id)

                journal_items.append((0, 0, vals))
                vals = self.generate_journal_items(False, journal_id, partner_account_id, 0, rec.reconcile, reconcile_id, period_id)
                journal_items.append((0, 0, vals))
                vals = self.generate_journal_items(False, journal_id, partner_account_id, 0, rec.balance, False, period_id)
                journal_items.append((0, 0, vals))

                rec.item_id.write({"reconcile_id": reconcile_id})

        return journal_items

    @api.multi
    def trigger_journal_entries(self):
        self.trigger_check_balance()

        account_id = self.get_account_id()
        partner_account_id = self.get_partner_account_id()
        reconcile_id = self.env["hos.reconcile"].create({})
        journal_id = self.get_journal_id()
        period_id = self.env["period.period"].get_period(self.date)

        journal_items = self.trigger_journal_items(account_id, partner_account_id, reconcile_id.id, journal_id, period_id)

        data = {"date": self.date,
                "period_id": period_id,
                "journal_id": journal_id,
                "reference": self.name,
                "progress": "posted",
                "journal_item": journal_items}

        self.env["journal.entries"].create(data)
        writter = "{0} Validated by {1} on {2}".format(self.payment_type.upper(), self.env.user.name, CURRENT_TIME)

        self.write({"progress": "posted", "writter": writter})

    @api.model
    def create(self, vals):
        code = "{0}{1}".format(self._name, vals["voucher_type"])
        vals["name"] = self.env["ir.sequence"].next_by_code(code)
        return super(Voucher, self).create(vals)

    @api.multi
    def mango(self):
        cr = []
        dr = []

        for rec in self.credit_lines:
            cr_obj = {}
            cr_obj["id"] = rec.id
            cr_obj["ref"] = "ff"
            cr_obj["amount"] = rec.amount

            cr.append(cr_obj)

        for rec in self.debit_lines:
            dr_obj = {}
            dr_obj["id"] = rec.id
            dr_obj["ref"] = "ff"
            dr_obj["amount"] = rec.amount

            dr.append(dr_obj)

        rex.reconciliation(cr, dr)




