# -*- coding: utf-8 -*-

from odoo import fields, models


# Leave Type
class LeaveType(models.Model):
    _name = "leave.type"

    name = fields.Char(string="Type", required=True)
    code = fields.Char(string="Code", required=True)
