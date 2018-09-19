# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"),
                 ("opened", "Position Opened"),
                 ("closed", "Position Closed")]


# Vacancy Position
class VacancyPosition(models.Model):
    _name = "vacancy.position"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", default=datetime.now().strftime("%Y-%m-%d"))
    position_id = fields.Many2one(comodel_name="hr.designation", string="Position", required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    roles = fields.Html(string="Roles & Responsibility")
    experience = fields.Html(string="Experience")
    preference = fields.Html(string="Preference")
    qualification = fields.Html(string="Qualification")
    comment = fields.Text(string="Comment")
    writter = fields.Text(string="Writter", track_visibility="always")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.multi
    def trigger_open(self):
        data = {"writter": "Vacancy position opened by {0}".format(self.env.user.name),
                "progress": "opened"}

        self.write(data)

    @api.multi
    def trigger_close(self):
        data = {"writter": "Vacancy position closed by {0}".format(self.env.user.name),
                "progress": "closed"}

        self.write(data)

    @api.model
    def create(self, vals):
        vals["writter"] = "Vacancy position created by {0}".format(self.env.user.name)
        vals["name"] = self.env['ir.sequence'].sudo().next_by_code(self._name)
        return super(VacancyPosition, self).create(vals)
