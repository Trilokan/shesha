# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

RECONCILE_TYPE = [("manual", "Manual"), ("automatic", "Automatic")]


# Leave Reconcile
class LeaveReconcile(models.Model):
    _name = "leave.reconcile"
    _inherit = "mail.thread"

    date = fields.Date(string="Date", default=datetime.now().strftime("%Y-%m-%d"))
    name = fields.Char(string="Name")
    reconcile_type = fields.Selection(selection=RECONCILE_TYPE, string="Type")
    writter = fields.Text(string="Writter", track_visibility="always")

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        vals["writter"] = "Leave Reconcile By {0}".format(self.env.user.company_id.id)
        return super(LeaveReconcile, self).create(vals)
