# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta


PROGRESS_INFO = [('draft', 'draft'), ('open', 'Open'), ('closed', 'Closed')]


# Week Schedule
class MonthAttendance(models.Model):
    _name = "month.attendance"
    _rec_name = "period_id"

    period_id = fields.Many2one(comodel_name="period.period", string="Month", required=True)
    month_detail = fields.One2many(comodel_name="time.attendance",
                                   inverse_name="month_id",
                                   string="Month Detail")
    progress = fields.Selection(PROGRESS_INFO, string='Progress', default="draft")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_period_id', 'unique (period_id)', 'Error! Month must be unique')]

    def get_days_in_month(self):
        from_date = self.period_id.from_date
        till_date = self.period_id.till_date

        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
        till_date_obj = datetime.strptime(till_date, "%Y-%m-%d")

        return (till_date_obj - from_date_obj).days

    def get_total_days(self, person):
        total_days = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                      ("attendance_id.month_id", "=", self.id),
                                                                      ("day_progress", "in",
                                                                       ["working_day", "holiday"])])

        return total_days

    def get_present_days(self, person):
        full_day = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                    ("attendance_id.month_id", "=", self.id),
                                                                    ("availability_progress", "=", "full_day")])

        half_day = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                    ("attendance_id.month_id", "=", self.id),
                                                                    ("availability_progress", "=", "half_day")])

        return full_day + (0.5 * half_day)

    def get_absent_days(self, person):
        absent = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                  ("attendance_id.month_id", "=", self.id),
                                                                  ("day_progress", "=", "working_day"),
                                                                  ("availability_progress", "=", "absent")])

        half_day = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                    ("attendance_id.month_id", "=", self.id),
                                                                    ("day_progress", "=", "working_day"),
                                                                    ("availability_progress", "=", "half_day")])

        return absent + (0.5 * half_day)

    def get_working_days(self, person):
        working_day = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                   ("attendance_id.month_id", "=", self.id),
                                                                   ("day_progress", "=", "working_day")])

        return working_day

    def get_holidays(self, person):
        holiday = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                   ("attendance_id.month_id", "=", self.id),
                                                                   ("day_progress", "=", "holiday")])

        return holiday

    def get_holidays_present(self, person):
        full_day = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                    ("attendance_id.month_id", "=", self.id),
                                                                    ("day_progress", "=", "holiday"),
                                                                    ("availability_progress", "=", "full_day")])

        half_day = self.env["time.attendance.detail"].search_count([("person_id", "=", person.id),
                                                                    ("attendance_id.month_id", "=", self.id),
                                                                    ("day_progress", "=", "holiday"),
                                                                    ("availability_progress", "=", "half_day")])

        return full_day + (0.5 * half_day)

    def get_lop_days(self, person):
        total = 0
        recs = self.env["leave.item"].search([("period_id", "=", self.period_id.id),
                                              ("person_id", "=", person.id),
                                              ("leave_account_id", "=", self.env.user.company_id.leave_lop_id.id)])

        for rec in recs:
            total = total + rec.credit

        return total

    def get_leave_available(self, person):
        employee_id = self.env["hr.employee"].search([("person_id", "=", person.id)])
        leave_account_id = employee_id.leave_account_id.id
        recs = self.env["leave.item"].search([("leave_account_id", "=", leave_account_id),
                                              ("debit", ">", 0),
                                              ("reconcile_id", "=", False)])

        available = 0
        for rec in recs:
            available = available + rec.debit

        return available

    def generate_header(self, date_list):
        header = ""

        header_list = ["Employee"] + date_list + ["Total Days",
                                                  "Present Days",
                                                  "Absent Days",
                                                  "Holidays",
                                                  "Holidays Present"]

        for rec in header_list:
            header = "{0}\n<th>{1}</th>".format(header, rec)

        header = "<tr>{0}</tr>".format(header)
        return header

    def generate_body(self, date_list, person_list):
        body = ""

        for person in person_list:
            person_id = self.env["hos.person"].search([("id", "=", person)])
            body = "{0}\n<tr><td>{1}</td>".format(body, person_id.name)

            for date in date_list:
                attendance = self.env["time.attendance.detail"].search([("person_id", "=", person),
                                                                        ("attendance_id.date", "=", date)])
                body = "{0}\n<td>{1}</td>".format(body, attendance.availability_progress)

            total_days = self.get_total_days(person_id)
            present_days = self.get_present_days(person_id)
            absent_days = self.get_absent_days(person_id)
            holidays = self.get_holidays(person_id)
            holiday_present = self.get_holidays_present(person_id)

            body = """{0}<td>{1}</td>
                         <td>{2}</td>
                         <td>{3}</td>
                         <td>{4}</td>
                         <td>{5}</td></tr>""".format(body,
                                                     total_days,
                                                     present_days,
                                                     absent_days,
                                                     holidays,
                                                     holiday_present)

        return body

    def trigger_preview(self):
        recs = self.month_detail

        date_list = []
        person_list = []
        for rec in recs:
            date_list.append(rec.date)

        recs = self.env["time.attendance.detail"].search([("attendance_id.month_id", "=", self.id)])

        for rec in recs:
            if rec.person_id.id not in person_list:
                person_list.append(rec.person_id.id)

        header = self.generate_header(date_list)
        body = self.generate_body(date_list, person_list)

        html = self.env.user.company_id.monthly_attendance_report
        report = html.format(header, body)

        view = self.env.ref('nagi.view_month_attendance_wiz_form')

        return {
            'name': 'Monthly Attendance',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'month.attendance.wiz',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'report': report}
        }

    @api.multi
    def trigger_closed(self):
        draft = self.env["time.attendance"].search_count([("month_id", "=", self.id), ("progress", "!=", "verified")])

        if draft:
            raise exceptions.ValidationError("Error! Daily attendance report is not verified")

        employees = self.env["hr.employee"].search([])

        for employee in employees:
            total_absent = self.get_absent_days(employee.person_id)

            voucher = {}
            voucher["period_id"] = self.period_id.id
            voucher["person_id"] = employee.person_id.id
            voucher["count"] = total_absent

            # Check already voucher is created
            check_voucher = self.env["leave.voucher"].search([("period_id", "=", self.period_id.id),
                                                              ("person_id", "=", employee.person_id.id)])

            if not check_voucher:
                voucher_id = self.env["leave.voucher"].create(voucher)
                voucher_id.get_cr_lines()
                voucher_id.update_count()
                voucher_id.trigger_posting()

        self.write({"progress": "closed"})

    @api.multi
    def trigger_open(self):
        if self.env["month.attendance"].search_count([("progress", "=", "open"), ("id", "!=", self.id)]):
            raise exceptions.ValidationError("Error! Please close all open months before open")

        # Leave Credits from leave configuration
        employees = self.env["hr.employee"].search([])

        for employee in employees:
            leave_item = []
            configs = self.env["leave.configuration"].search([("leave_level_id", "=", employee.leave_level_id.id)])

            # Credit Detail - Employee
            for config in configs:
                journal_detail = {}
                journal_detail["period_id"] = self.period_id.id
                journal_detail["person_id"] = employee.person_id.id
                journal_detail["leave_account_id"] = employee.leave_account_id.id
                journal_detail["description"] = "{0} Leave Credit".format(config.leave_type_id.name)
                journal_detail["debit"] = config.leave_credit
                journal_detail["reference"] = self.period_id.name
                journal_detail["leave_order"] = config.leave_order

                leave_item.append((0, 0, journal_detail))

            # Credit Detail - Monthly
            for config in configs:
                journal_detail = {}
                journal_detail["period_id"] = self.period_id.id
                journal_detail["person_id"] = employee.person_id.id
                journal_detail["leave_account_id"] = self.env.user.company_id.leave_credit_id.id
                journal_detail["description"] = "Leave Credit"
                journal_detail["credit"] = config.leave_credit
                journal_detail["reference"] = self.period_id.name
                journal_detail["leave_order"] = config.leave_order

                leave_item.append((0, 0, journal_detail))

            journal = {}
            journal["period_id"] = self.period_id.id
            journal["person_id"] = employee.person_id.id
            journal["journal_detail"] = leave_item
            journal["progress"] = "posted"
            journal["reference"] = self.period_id.name

            self.env["leave.journal"].create(journal)

        self.write({"progress": "open"})

