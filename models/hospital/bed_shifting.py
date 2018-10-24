# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

PROGRESS = [("draft", "Draft"), ("shifted", "Shifted")]

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")


class BedShifting(models.Model):
    _name = "bed.shifting"

    treatment_id = fields.Many2one(comodel_name="hos.treatment", string="Patient", required=True)
    date = fields.Datetime(string="Date", required=True, default=CURRENT_TIME)
    source_id = fields.Many2one(comodel_name="hos.bed", string="From Location", required=True)
    destination_id = fields.Many2one(comodel_name="hos.bed", string="To Location", required=True)
    progress = fields.Selection(selection=PROGRESS, string="Progress", default="draft")
