# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta


PROGRESS_INFO = [('draft', 'Draft'), ('verified', 'Verified')]
AVAIL_PROGRESS = [('full_day', 'Full Day'), ('half_day', 'Half Day'), ('absent', 'Absent')]
DAY_PROGRESS = [('holiday', 'Holiday'), ('working_day', 'Working Day')]


# Attendance
class TimeAttendance(models.Model):
    _name = "time.attendance"
    _rec_name = "date"

    date = fields.Date(string="Date", readonly=True)
    month_id = fields.Many2one(comodel_name="month.attendance", string="Month", readonly=True)
    attendance_detail = fields.One2many(comodel_name="time.attendance.detail",
                                        inverse_name="attendance_id",
                                        string="Attendance Detail")
    progress = fields.Selection(PROGRESS_INFO, string='Progress', default="draft")

    present = fields.Integer(string="Present", readonly=True)
    half_day_present = fields.Integer(string="Half Day Present", readonly=True)
    absent = fields.Integer(string="Absent", readonly=True)
    employee_count = fields.Integer(string="Employee Count", readonly=True)
    week_off_count = fields.Integer(string="Week-Off Count", readonly=True)
    working_count = fields.Integer(string="Working Count", readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.multi
    def trigger_progress(self):
        self.get_availability_progress()
        self.get_report()

    @api.multi
    def trigger_verify(self):
        self.trigger_progress()
        data = {"progress": "verified"}
        self.write(data)

    @api.multi
    def get_report(self):
        rec_obj = self.env["time.attendance.detail"]
        self.employee_count = rec_obj.search_count([("attendance_id", "=", self.id)])
        self.week_off_count = rec_obj.search_count([("day_progress", "=", "holiday"), ("attendance_id", "=", self.id)])
        self.working_count = rec_obj.search_count([("day_progress", "=", "working_day"), ("attendance_id", "=", self.id)])
        self.present = rec_obj.search_count([("availability_progress", "=", "full_day"), ("attendance_id", "=", self.id)])
        self.half_day_present = rec_obj.search_count([("availability_progress", "=", "half_day"), ("attendance_id", "=", self.id)])
        self.absent = rec_obj.search_count([("availability_progress", "=", "absent"), ("attendance_id", "=", self.id)])

    @api.multi
    def get_availability_progress(self):
        recs = self.attendance_detail

        for rec in recs:
            rec.update_hours()
            rec.trigger_get_availability_progress()

    _sql_constraints = [('unique_attendance',
                         'unique (date)',
                         'Error! Date should not be repeated')]


class TimeAttendanceDetail(models.Model):
    _name = "time.attendance.detail"

    shift_id = fields.Many2one(comodel_name="time.shift", string="Shift", readonly=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Employee", readonly=True)
    attendance_id = fields.Many2one(comodel_name="time.attendance", string="Attendance", readonly=True)
    expected_from_time = fields.Datetime(string="Expected From Time", readonly=True)
    actual_from_time = fields.Datetime(string="Actual From Time", readonly=True)
    expected_till_time = fields.Datetime(string="Expected Till Time", readonly=True)
    actual_till_time = fields.Datetime(string="Actual Till Time", readonly=True)
    expected_hours = fields.Float(string="Expected Hours", default=0, readonly=True)
    actual_hours = fields.Float(string="Actual Hours", default=0, readonly=True)
    day_progress = fields.Selection(DAY_PROGRESS, string='Day Status', readonly=True)
    availability_progress = fields.Selection(AVAIL_PROGRESS, string='Availability Status')
    progress = fields.Selection(PROGRESS_INFO, string='Progress', related='attendance_id.progress')
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.multi
    def update_hours(self):
        if self.expected_from_time and self.expected_till_time:
            expected_from_time = datetime.strptime(self.expected_from_time, "%Y-%m-%d %H:%M:%S")
            expected_till_time = datetime.strptime(self.expected_till_time, "%Y-%m-%d %H:%M:%S")
            self.expected_hours = (expected_till_time - expected_from_time).total_seconds()/(60 * 60)

        if self.actual_from_time and self.actual_till_time:
            actual_from_time = datetime.strptime(self.actual_from_time, "%Y-%m-%d %H:%M:%S")
            actual_till_time = datetime.strptime(self.actual_till_time, "%Y-%m-%d %H:%M:%S")
            self.actual_hours = (actual_till_time - actual_from_time).total_seconds() / (60 * 60)

    @api.multi
    def trigger_get_availability_progress(self):
        full_day = self.env["time.configuration"].search([('name', '=', 'Full Day')])
        half_day = self.env["time.configuration"].search([('name', '=', 'Half Day')])
        if self.actual_hours >= full_day.value:
            self.availability_progress = "full_day"
        elif self.actual_hours >= half_day.value:
            self.availability_progress = "half_day"
        else:
            self.availability_progress = "absent"

    _sql_constraints = [('unique_attendance_detail',
                         'unique (attendance_id, person_id)',
                         'Error! Employee should not repeated')]
