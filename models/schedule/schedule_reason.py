# -*- coding: utf-8 -*-

from odoo import models, fields


class ScheduleReason(models.Model):
    _name = "schedule.reason"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)


