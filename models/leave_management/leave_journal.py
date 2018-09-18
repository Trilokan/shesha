# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("posted", "Posted")]


# Journal Entry
class LeaveJournal(models.Model):
    _name = "leave.journal"

    date = fields.Date(string="Date", required=True, default=datetime.now().strftime("%Y-%m-%d"))
    period_id = fields.Many2one(comodel_name="period.period", string="Period", required=True)
    name = fields.Char(string="Name", readonly=True)
    reference = fields.Char(string="Reference")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Person")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    journal_detail = fields.One2many(comodel_name="leave.item",
                                     inverse_name="journal_id",
                                     string="Journal Entry Detail")

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(LeaveJournal, self).create(vals)
