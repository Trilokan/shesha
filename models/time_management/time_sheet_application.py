# -*- coding: utf-8 -*-

from odoo import fields, api, exceptions, models, _
from datetime import datetime, timedelta


# Time Sheet Application
class TimeSheetApplication(models.TransientModel):
    _name = "time.sheet.application"

    date = fields.Datetime(string="Date")

    @api.multi
    def trigger_employee_in(self):

        data = {"person_id": self.env.user.person_id.id,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "progress": "in",
                "process": "automatic"}

        self.env["time.sheet"].create(data)

    @api.multi
    def trigger_employee_out(self):

        data = {"person_id": self.env.user.person_id.id,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "progress": "out",
                "process": "automatic"}

        self.env["time.sheet"].create(data)
