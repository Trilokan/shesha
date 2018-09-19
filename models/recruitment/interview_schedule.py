# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime

SCHEDULE_INFO = [("draft", "Draft"),
                 ("on_process", "On Process"),
                 ("cancelled", "Cancelled"),
                 ("completed", "Completed")]

SCHEDULE_DETAIL_INFO = [("selected", "Selected"),
                        ("rejected", "Rejected"),
                        ("on_hold", "On Hold")]


# Interview Schedule
class InterviewSchedule(models.Model):
    _name = "interview.schedule"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", required=True, default=datetime.now().strftime("%Y-%m-%d"))
    vacancy_id = fields.Many2one(comodel_name="vacancy.position", string="Vacancy Position", required=True)
    designation_id = fields.Many2one(comodel_name="hr.designation", string="Designation")
    progress = fields.Selection(selection=SCHEDULE_INFO, string="Progress", default='draft')
    previous_interview = fields.Many2one(comodel_name="interview.schedule", string="Previous Interview")
    scheduled_detail = fields.One2many(comodel_name="interview.schedule.detail",
                                       string="Scheduled Detail",
                                       inverse_name="scheduled_id")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    writter = fields.Text(string="Writter", track_visibility="always")

    @api.multi
    def trigger_confirm(self):
        data = {"writter": "Interview schedule confirmed by {0}".format(self.env.user.name),
                "progress": "on_process"}

        if not self.scheduled_detail:
            raise exceptions.ValidationError("Error! No Resumes found")

        self.write(data)

    @api.multi
    def trigger_cancel(self):
        data = {"writter": "Interview schedule cancelled by {0}".format(self.env.user.name),
                "progress": "cancelled"}
        self.write(data)

    @api.multi
    def trigger_completed(self):
        data = {"writter": "Interview Schedule completed by {0}".format(self.env.user.name),
                "progress": "completed"}
        self.write(data)

    @api.model
    def create(self, vals):
        vals["writter"] = "Interview schedule created by {0}".format(self.env.user.name)
        return super(InterviewSchedule, self).create(vals)


class InterviewScheduledDetail(models.Model):
    _name = "interview.schedule.detail"
    _inherit = "mail.thread"

    resume_id = fields.Many2one(comodel_name="resume.bank", string="Candidate", required=True)
    candidate_uid = fields.Char(string="Candidate ID", related="resume_id.candidate_uid")
    scheduled_id = fields.Many2one(comodel_name="interview.schedule", string="Interview")
    status = fields.Selection(selection=SCHEDULE_DETAIL_INFO, string="Status")
    progress = fields.Selection(SCHEDULE_INFO, string='Progress', related='scheduled_id.progress')

