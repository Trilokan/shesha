# -*- coding: utf-8 -*-

from odoo import models, fields


# Journal
class Journal(models.Model):
    _name = "hos.journal"

    name = fields.Char(string="Journal", required=True)
    code = fields.Char(string="Code", required=True)
