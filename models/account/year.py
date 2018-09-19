# -*- coding: utf-8 -GPK*-

from odoo import models, fields, api, exceptions

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed")]


class Year(models.Model):
    _name = "year.year"
    _rec_name = "name"

    name = fields.Char(string="Year", required=True)
    financial_year = fields.Char(string="Financial Year", required=True)
    period_detail = fields.One2many(comodel_name="period.period",
                                    inverse_name="year_id",
                                    string="Period",
                                    readonly=True)

    _sql_constraints = [('unique_year', 'unique (name)', 'Error! Year must be unique'),
                        ('unique_financial_year', 'unique (financial_year)', 'Error! Financial Year must be unique')]
