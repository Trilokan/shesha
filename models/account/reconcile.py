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

    def reconciliation(self, cr_obj, dr_obj):
        for cr in cr_obj:
            value = (cr.amount - cr.reconcile)

            for dr in dr_obj:
                diff = dr.amount - dr.reconcile

                if (diff > 0) and (value > 0):

                    # self.env["hos.reconcile"].create()
                    print diff, value
                    if diff >= value:
                        dr.reconcile = dr.reconcile + value
                        cr.reconcile = cr.reconcile + value
                    else:
                        dr.reconcile = dr.reconcile + diff
                        cr.reconcile = cr.reconcile + diff

                    cr.balance = cr.amount - cr.reconcile
                    dr.balance = dr.amount - dr.reconcile
                    cr.status = dr.status = True

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(Reconcile, self).create(vals)
