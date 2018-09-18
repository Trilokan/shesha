# -*- coding: utf-8 -*-

from odoo import fields, api, exceptions, models

# Payslip

PROGRESS_INFO = [('draft', 'Draft'), ('generated', 'Generated')]
PAY_TYPE = [('allowance', 'Allowance'), ('deduction', 'Deduction')]


class MonthAttendanceWiz(models.TransientModel):
    _name = "month.attendance.wiz"

    report = fields.Html(string="Report",
                         readonly=True,
                         default=lambda self: self.env.context.get('report', False))


