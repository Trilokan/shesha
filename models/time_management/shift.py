# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta

END_INFO = [('current_day', 'Current Day'), ('next_day', 'Next Day')]


# Shift Master
class Shift(models.Model):
    _name = "time.shift"
    _inherit = "mail.thread"

    name = fields.Char(string="Shift", required=True)
    total_hours = fields.Float(string="Total Hours", readonly=True)
    from_total_hours = fields.Float(string="From Total Hours", compute="_get_from_hours")
    till_total_hours = fields.Float(string="Till Total Hours", compute="_get_till_hours")
    end_day = fields.Selection(selection=END_INFO, string="Ends On", default="current_day")
    from_hours = fields.Integer(string="From Hours")
    from_minutes = fields.Integer(string="From Minutes")
    till_hours = fields.Integer(string="Till Hours")
    till_minutes = fields.Integer(string="Till Minutes")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    def _get_from_hours(self):
        today = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        for rec in self:
            from_date = today + timedelta(hours=rec.from_hours) + timedelta(minutes=rec.from_minutes)

            secs = (from_date - today).seconds

            minutes = ((secs / 60) % 60) / 60.0
            hours = secs / 3600

            rec.from_total_hours = hours + minutes

    def _get_till_hours(self):
        today = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        for rec in self:
            till_date = today + timedelta(hours=rec.till_hours) + timedelta(minutes=rec.till_minutes)

            if rec.end_day == 'next_day':
                till_date = till_date + timedelta(days=1)

            secs = (till_date - today).seconds

            minutes = ((secs / 60) % 60) / 60.0
            hours = secs / 3600

            rec.till_total_hours = hours + minutes

    @api.multi
    def trigger_calculate(self):

        today = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

        from_date = today + timedelta(hours=self.from_hours) + timedelta(minutes=self.from_minutes)
        till_date = today + timedelta(hours=self.till_hours) + timedelta(minutes=self.till_minutes)

        if self.end_day == 'next_day':
            till_date = till_date + timedelta(days=1)

        secs = (till_date - from_date).seconds

        minutes = ((secs / 60) % 60) / 60.0
        hours = secs / 3600

        self.total_hours = hours + minutes

