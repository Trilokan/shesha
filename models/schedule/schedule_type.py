# -*- coding: utf-8 -*-

from odoo import models, fields


class ScheduleType(models.Model):
    _name = "schedule.type"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)


