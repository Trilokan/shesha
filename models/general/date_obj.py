# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta

PROGRESS_INFO = [('draft', 'Draft'), ('scheduled', 'Scheduled')]
TIME_DELAY_HRS = 5.50


# Week Schedule
class ModelDate(models.Model):
    _name = "model.date"

    def from_date_greater(self, from_date, till_date, date_format):

        from_obj = datetime.strptime(from_date, date_format)
        till_obj = datetime.strptime(till_date, date_format)

        return True if from_obj > till_obj else False

    def date_difference(self, from_date, till_date, date_format):
        from_obj = datetime.strptime(from_date, date_format)
        till_obj = datetime.strptime(till_date, date_format)

        return (till_obj - from_obj).days + 1

    def date_list(self, from_date, till_date, date_format):
        result = []
        day_difference = self.date_difference(from_date, till_date, date_format)

        for day in range(0, day_difference):
            date_obj = datetime.strptime(from_date, date_format) + timedelta(days=day)
            result.append(date_obj.strftime(date_format))

        return result

    def get_expected_time(self, obj, hours, minutes, total_hrs):
        data = {"from_time": obj + timedelta(hours=hours, minutes=minutes),
                "till_time": obj + timedelta(hours=hours + total_hrs, minutes=minutes)}

        return data

