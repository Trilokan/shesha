# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Diagnosis(models.Model):
    _name = "patient.diagnosis"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
