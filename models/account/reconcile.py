# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

RECONCILE_TYPE = [("manual", "Manual"), ("auto", "Automatic")]


class Reconcile(models.Model):
    _name = "hos.reconcile"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", default=CURRENT_DATE)
    reconcile_type = fields.Selection(selection=RECONCILE_TYPE, string="Reconcile Type", default="auto")

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(Reconcile, self).create(vals)
