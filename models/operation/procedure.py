# -*- coding: utf-8 -*-

from odoo import fields, api, exceptions, _, models
from datetime import datetime, timedelta
from .. import calculation


PROGRESS_INFO = [('draft', 'Draft'), ('approved', 'approved'), ('cancel', 'Cancel')]


# Operation Theater procedure
class OTProcedure(models.Model):
    _name = "ot.procedure"

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    procedure = fields.Html(string="procedure")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")


