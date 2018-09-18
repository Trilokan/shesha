# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("posted", "Posted")]


# Journal Entry Detail
class LeaveItem(models.Model):
    _name = "leave.item"

    date = fields.Date(string="Date", required=True, default=datetime.now().strftime("%Y-%m-%d"))
    period_id = fields.Many2one(comodel_name="period.period", string="Period", required=True)
    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    reference = fields.Char(string="Reference")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Person")
    credit = fields.Float(string="Credit")
    debit = fields.Float(string="Debit")
    reconcile_id = fields.Many2one(comodel_name="leave.reconcile", string="Reconcile")
    leave_account_id = fields.Many2one(comodel_name="leave.account", string="Account")
    journal_id = fields.Many2one(comodel_name="leave.journal", string="Journal Entry")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", related="journal_id.progress")
    comment = fields.Text(string="Comment")
    leave_order = fields.Integer(string="Leave Order", default=0)

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(LeaveItem, self).create(vals)
