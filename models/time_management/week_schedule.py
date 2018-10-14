# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta

PROGRESS_INFO = [('draft', 'Draft'), ('scheduled', 'Scheduled')]
TIME_DELAY_HRS = -5
TIME_DELAY_MIN = -30


# Week Schedule
class WeekSchedule(models.Model):
    _name = "week.schedule"
    _inherit = "mail.thread"

    from_date = fields.Date(string="From Date", required=True)
    till_date = fields.Date(string="Till Date", required=True)
    schedule_detail = fields.One2many(comodel_name="week.schedule.detail",
                                      inverse_name="schedule_id",
                                      string="Schedule Detail")
    off_detail = fields.One2many(comodel_name="week.off.detail",
                                 inverse_name="schedule_id",
                                 string="Week-Off Detail")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    writter = fields.Text(string="Writter", track_visibility="always")

    def check_lines(self):
        if not self.schedule_detail:
            raise exceptions.ValidationError("Error! Atleast One employee required for schedule approve")

    @api.constrains("from_date", "till_date")
    def check_date(self):
        """ From Date < Till Date """
        date_greater = self.env["model.date"].from_date_greater(self.from_date, self.till_date, "%Y-%m-%d")
        if date_greater:
            raise exceptions.ValidationError("Error! From Date should be greater than Till Date")

        days = self.env["model.date"].date_difference(self.from_date, self.till_date, "%Y-%m-%d")
        if days != 7:
            raise exceptions.ValidationError("Error! From Date and Till Date should be within a week")

        from_date = datetime.strptime(self.from_date, "%Y-%m-%d")
        if from_date.weekday() != 0:
            raise exceptions.ValidationError("Error! Week should start from Monday")

        week_schedule = self.env["week.schedule"].search_count([("from_date", "=", self.from_date)])
        if week_schedule > 1:
            raise exceptions.ValidationError("Error! Duplicate Week Schedule")

    def generate_attendance(self):
        date_range = self.env["model.date"].date_list(self.from_date, self.till_date, "%Y-%m-%d")

        for date in date_range:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            attendance_detail = self.get_model_line_data(date_obj, date)
            attendance = self.get_model_data(date, attendance_detail)

            self.env["time.attendance"].create(attendance)

    def get_model_data(self, date, attendance_detail):
        month_id = self.env["month.attendance"].search([("period_id.from_date", "<=", date),
                                                        ("period_id.till_date", ">=", date)])

        if not month_id:
            raise exceptions.ValidationError("Error! Attendance Month is not set")

        return {"date": date, "month_id": month_id.id, "attendance_detail": attendance_detail}

    def get_model_line_data(self, obj, date):
        attendance_detail = []

        recs = self.schedule_detail
        for rec in recs:
            timings = self.env["model.date"].get_expected_time(obj,
                                                               rec.shift_id.from_hours + TIME_DELAY_HRS,
                                                               rec.shift_id.from_minutes + TIME_DELAY_MIN,
                                                               rec.shift_id.total_hours)
            for person_id in rec.person_ids:
                record_data = {"shift_id": rec.shift_id.id,
                               "person_id": person_id.id,
                               "day_progress": self.get_day_progress(date, person_id.id),
                               "expected_from_time": timings["from_time"],
                               "expected_till_time": timings["till_time"]}

                attendance_detail.append((0, 0, record_data))

        return attendance_detail

    def get_day_progress(self, current_date, person_id):
        holiday = self.env["week.off.detail"].search([("date", "=", current_date),
                                                      ("person_ids", "=", person_id),
                                                      ("schedule_id", "=", self.id)])

        return "holiday" if holiday else "working_day"

    @api.multi
    def trigger_schedule(self):
        self.check_lines()
        self.check_date()
        self.generate_attendance()
        self.write({'progress': 'scheduled'})

    @api.constrains('schedule_detail', 'off_detail')
    def check_employee_duplication(self):
        recs = self.schedule_detail

        person_list = []
        for rec in recs:
            for person_id in rec.person_ids:
                if person_id.id in person_list:
                    raise exceptions.ValidationError("Error! Employee {0} assign to multiple shift".format(person_id.name))
                person_list.append(person_id.id)

        recs = self.off_detail

        for rec in recs:
            if (self.from_date > rec.date) or (rec.date > self.till_date):
                raise exceptions.ValidationError("Error! Week-Off date must be within a week")


class WeekScheduleDetail(models.Model):
    _name = "week.schedule.detail"

    shift_id = fields.Many2one(comodel_name="time.shift", string="Shift", required=True)
    person_ids = fields.Many2many(comodel_name="hos.person", string="Employee", required=True,
                                  domain=[("is_employee", "=", True)])
    schedule_id = fields.Many2one(comodel_name="week.schedule", string="Schedule")
    progress = fields.Selection(PROGRESS_INFO, string='Progress', related='schedule_id.progress')
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)


class WeekOffDetail(models.Model):
    _name = "week.off.detail"

    date = fields.Date(string="Date", required=True)
    person_ids = fields.Many2many(comodel_name="hos.person", string="Employee", required=True,
                                  domain=[("is_employee", "=", True)])
    schedule_id = fields.Many2one(comodel_name="week.schedule", string="Schedule")
    progress = fields.Selection(PROGRESS_INFO, string='Progress', related='schedule_id.progress')
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
