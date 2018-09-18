# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta

PROGRESS_INFO = [('draft', 'Draft'), ('changed', 'Changed')]
DAY_PROGRESS = [('holiday', 'Holiday'), ('working_day', 'Working Day')]


# Attendance Change
class AttendanceChange(models.Model):
    _name = "attendance.change"
    _inherit = "mail.thread"

    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    reason = fields.Text(string="Reason", required=True)

    progress = fields.Selection(selection=PROGRESS_INFO,
                                string="Progress",
                                default="draft",
                                track_visibility='always')
    person_id = fields.Many2one(comodel_name="hos.person",
                                string="Employee")
    shift_id = fields.Many2one(comodel_name="time.shift", string="Shift", required=True)
    day_progress = fields.Selection(DAY_PROGRESS, string='Day Status', required=True)

    def check_month(self):
        attendance = self.env["time.attendance.detail"].search([("person_id", "=", self.person_id.id),
                                                                ("attendance_id.date", "=", self.date)])

        if attendance:
            if attendance.attendance_id.month_id.progress == "closed":
                raise exceptions.ValidationError("Error! Month is already closed")
        else:
            raise exceptions.ValidationError("Error! please check")

    def trigger_holiday_change(self):
        attendance = self.env["time.attendance.detail"].search([("person_id", "=", self.person_id.id),
                                                                ("attendance_id.date", "=", self.date)])

        attendance.write({"day_progress": self.day_progress})
        self.write({"progress": "changed"})

    def trigger_shift_change(self):
        pass

    def update_attendance(self):
        current_date_obj = datetime.strptime(self.date, "%Y-%m-%d")
        next_date_obj = current_date_obj + timedelta(days=1)
        next_date = next_date_obj.strftime("%Y-%m-%d")

        attendance = self.env["time.attendance.detail"].search([("person_id", "=", self.person_id.id),
                                                                ("attendance_id.date", "=", self.date)])

        if attendance:
            if attendance.attendance_id.month_id.progress == "closed":
                raise exceptions.ValidationError("Error! Month is already closed")

            expected_from_time = "{0} {1}:{2}:00".format(self.date,
                                                         self.shift_id.from_hours,
                                                         self.shift_id.from_minutes)
            if self.shift_id.end_day == 'current_day':
                expected_till_time = "{0} {1}:{2}:00".format(self.date,
                                                             self.shift_id.till_hours,
                                                             self.shift_id.till_minutes)
            elif self.shift_id.end_day == 'next_day':
                expected_till_time = "{0} {1}:{2}:00".format(self.date,
                                                             self.shift_id.till_hours,
                                                             self.shift_id.till_minutes)

            new_from_time_obj = datetime.strptime(expected_from_time, "%Y-%m-%d %H:%M:%S") - timedelta(
                minutes=(TIME_DELAY_HRS * 60) + TIME_DELAY_MIN)
            new_till_time_obj = datetime.strptime(expected_till_time, "%Y-%m-%d %H:%M:%S") - timedelta(
                minutes=(TIME_DELAY_HRS * 60) + TIME_DELAY_MIN)

            attendance.write({"shift_id": self.shift_id.id,
                              "expected_from_time": new_from_time_obj,
                              "expected_till_time": new_till_time_obj})
        else:
            raise exceptions.ValidationError("Error! please check")


