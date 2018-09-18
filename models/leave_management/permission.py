# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime

PROGRESS_INFO = [('draft', 'Draft'),
                 ('confirmed', 'Waiting For Approval'),
                 ('cancelled', 'Cancelled'),
                 ('approved', 'Approved')]


# Permission
class Permission(models.Model):
    _name = "permission.application"
    _inherit = "mail.thread"

    from_time = fields.Datetime(string="From",
                                default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                required=True)
    till_time = fields.Datetime(string="Till",
                                default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                required=True)
    person_id = fields.Many2one(comodel_name="hos.person",
                                string="Employee",
                                default=lambda self: self.env.user.person_id.id,
                                readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    reason = fields.Text(string="Reason", required=True)
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")

    def check_month(self):
        attendance = self.env["time.attendance.detail"].search([("attendance_id.date", "=", self.from_date)])

        if attendance:
            if attendance.attendance_id.month_id.progress == "closed":
                raise exceptions.ValidationError("Error! Month is already closed")

    @api.multi
    def trigger_confirmed(self):
        self.check_month()
        data = {"progress": "confirmed",
                "writter": "Permission confirmed by {0}".format(self.env.user.name)}

        self.write(data)

    @api.multi
    def trigger_cancelled(self):
        self.check_month()
        data = {"progress": "cancelled",
                "writter": "Permission cancelled by {0}".format(self.env.user.name)}

        self.write(data)

    @api.multi
    def trigger_approved(self):
        self.check_month()
        data = {"progress": "approved",
                "writter": "Permission approved by {0}".format(self.env.user.name)}

        self.write(data)

    @api.model
    def create(self, vals):
        self.check_month()
        vals["writter"] = "Permission created by {0}".format(self.env.user.name)
        return super(Permission, self).create(vals)
