# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BedStatus(models.TransientModel):
    _name = "bed.status"

    bed_count = fields.Integer(string="Total Bed")
    occupied_count = fields.Integer(string="Occupied")
    vacant_count = fields.Integer(string="Vacant")







