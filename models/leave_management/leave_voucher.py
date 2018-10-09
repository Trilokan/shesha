# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("posted", "Posted")]
VOUCHER_INFO = [("credit", "Credit"), ("debit", "Debit")]


# Leave Voucher
class LeaveVoucher(models.Model):
    _name = "leave.voucher"
    _inherit = "mail.thread"

    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       required=True)
    name = fields.Char(string="Name", readonly=True)
    period_id = fields.Many2one(comodel_name="period.period", string="Period", required=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Person", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    count = fields.Float(string="Count")
    difference = fields.Float(string="Difference")
    voucher_detail = fields.One2many(comodel_name="leave.voucher.line",
                                     inverse_name="voucher_id",
                                     string="Leave Voucher Line")

    is_manual = fields.Boolean(string="Is Manual")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")

    @api.onchange("count")
    def update_count(self):
        recs = self.voucher_detail

        count = self.count

        for rec in recs:
            rec.reconcile = False
            rec.leave_reconcile = 0

        for rec in recs:
            diff = rec.leave_available - rec.leave_reconcile
            if (diff > 0) and (count > 0):
                if diff >= count:
                    rec.leave_reconcile = rec.leave_reconcile + count
                    count = 0
                    rec.reconcile = True

                elif diff < count:
                    rec.reconcile = True
                    rec.leave_reconcile = rec.leave_reconcile + diff
                    count = count - diff

        self.difference = count

    def check_pending(self):
        pending = self.env["leave.voucher"].search_count([("person_id", "=", self.person_id.id),
                                                          ("progress", "=", "draft")])

        if pending > 1:
            raise exceptions.ValidationError("Error! Some records in pending please check")

        duplicate = self.env["leave.voucher"].search_count([("person_id", "=", self.person_id.id),
                                                            ("period_id", "=", self.period_id.id)])

        if duplicate > 1:
            raise exceptions.ValidationError("Error! Duplicate please check")

    @api.onchange("person_id")
    def get_cr_lines(self):
        if self.person_id:

            self.check_pending()
            self.voucher_detail.unlink()
            res_cr = []

            employee_id = self.env["hr.employee"].search([("person_id", "=", self.person_id.id)])
            leave_account_id = employee_id.leave_account_id.id

            recs = self.env["leave.item"].search([("leave_account_id", "=", leave_account_id),
                                                  ("debit", ">", 0),
                                                  ("reconcile_id", "=", False)])

            recs.sorted(key=lambda r: r.leave_order)

            for rec in recs:
                data = {}

                data["date"] = rec.date
                data["name"] = rec.name
                data["person_id"] = self.person_id.id
                data["description"] = rec.description
                data["leave_available"] = rec.debit
                data["item_id"] = rec.id
                data["voucher_type"] = "credit"
                data["leave_order"] = rec.leave_order
                res_cr.append(data)

            self.voucher_detail = res_cr

    def generate_journal_leave_debit(self):
        leave_item = []

        journal_detail = {}

        journal_detail["date"] = datetime.now().strftime("%Y-%m-%d")
        journal_detail["period_id"] = self.period_id.id
        journal_detail["name"] = self.env['ir.sequence'].next_by_code("leave.item")
        journal_detail["company_id"] = self.env.user.company_id.id
        journal_detail["person_id"] = self.person_id.id
        journal_detail["description"] = "Leave Debit"
        journal_detail["debit"] = self.count
        journal_detail["leave_account_id"] = self.env.user.company_id.leave_debit_id.id

        leave_item.append((0, 0, journal_detail))

        return leave_item

    def generate_journal_leave_lop(self):
        leave_item = []

        journal_detail = {}
        journal_detail["date"] = datetime.now().strftime("%Y-%m-%d")
        journal_detail["period_id"] = self.period_id.id
        journal_detail["name"] = self.env['ir.sequence'].next_by_code("leave.item")
        journal_detail["company_id"] = self.env.user.company_id.id
        journal_detail["person_id"] = self.person_id.id
        journal_detail["description"] = "Leave Debit"
        journal_detail["credit"] = self.difference
        journal_detail["leave_account_id"] = self.env.user.company_id.leave_lop_id.id

        leave_item.append((0, 0, journal_detail))

        return leave_item

    def generate_journal_leave_credit(self, reconcile_id):
        leave_item = []
        # Create Journal for reconcillation
        recs = self.voucher_detail

        employee_id = self.env["hr.employee"].search([("person_id", "=", self.person_id.id)])

        for rec in recs:
            if rec.reconcile and (rec.leave_reconcile > 0):
                rec.item_id.write({"reconcile_id": reconcile_id.id})

                journal_detail = {}
                journal_detail["date"] = datetime.now().strftime("%Y-%m-%d")
                journal_detail["period_id"] = self.period_id.id
                journal_detail["name"] = self.env['ir.sequence'].next_by_code("leave.item")
                journal_detail["company_id"] = self.env.user.company_id.id
                journal_detail["person_id"] = self.person_id.id
                journal_detail["description"] = "Leave Debit"
                journal_detail["credit"] = rec.leave_available
                journal_detail["leave_account_id"] = employee_id.leave_account_id.id
                journal_detail["reconcile_id"] = reconcile_id.id

                leave_item.append((0, 0, journal_detail))

                if (rec.leave_reconcile > 0) and ((rec.leave_available - rec.leave_reconcile) > 0):
                    rec.item_id.write({"reconcile_id": reconcile_id.id})

                    journal_detail = {}
                    journal_detail["date"] = datetime.now().strftime("%Y-%m-%d")
                    journal_detail["period_id"] = self.period_id.id
                    journal_detail["name"] = self.env['ir.sequence'].next_by_code("leave.item")
                    journal_detail["company_id"] = self.env.user.company_id.id
                    journal_detail["person_id"] = self.person_id.id
                    journal_detail["description"] = "Leave Debit"
                    journal_detail["debit"] = rec.leave_available - rec.leave_reconcile
                    journal_detail["leave_account_id"] = employee_id.leave_account_id.id
                    journal_detail["leave_order"] = rec.leave_order

                    leave_item.append((0, 0, journal_detail))

        return leave_item

    @api.multi
    def generate_journal(self):
        leave_item = []
        reconcile_id = self.env["leave.reconcile"].create({})

        debit = self.generate_journal_leave_debit()
        lop = self.generate_journal_leave_lop()
        credit = self.generate_journal_leave_credit(reconcile_id)

        leave_item.extend(debit)
        leave_item.extend(lop)
        leave_item.extend(credit)

        journal = {}

        journal["date"] = datetime.now().strftime("%Y-%m-%d")
        journal["period_id"] = self.period_id.id
        journal["name"] = self.env['ir.sequence'].next_by_code("leave.journal")
        journal["company_id"] = self.env.user.company_id.id
        journal["person_id"] = self.person_id.id
        journal["journal_detail"] = leave_item
        journal["progress"] = "posted"

        self.env["leave.journal"].create(journal)

    @api.multi
    def trigger_posting(self):
        self.generate_journal()
        data = {"progress": "posted",
                "writter": "Leave Voucher posted by {0}".format(self.env.user.name)}

        self.write(data)

    def default_vals_creation(self, vals):
        vals["company_id"] = self.env.user.company_id.id
        vals["writter"] = "Leave Voucher created by {0}".format(self.env.user.name)
        vals["name"] = self.env['ir.sequence'].next_by_code("leave.voucher")
        return vals


class LeaveVoucherLine(models.Model):
    _name = "leave.voucher.line"
    _inherit = "mail.thread"

    date = fields.Date(string="Date", required=True)
    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    item_id = fields.Many2one(comodel_name="leave.item", string="Journal Item")
    person_id = fields.Many2one(comodel_name="hos.person", string="Person")
    voucher_id = fields.Many2one(comodel_name="leave.voucher", string="Leave Voucher")
    leave_available = fields.Float(string="Leave Available")
    reconcile = fields.Boolean(string="Reconcile")
    leave_reconcile = fields.Float(string="Leave Reconcile")
    leave_order = fields.Float(string="Leave Order")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True)
    writter = fields.Text(string="Writter", track_visibility="always")

