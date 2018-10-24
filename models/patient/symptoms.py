# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Symptoms(models.Model):
    _name = "patient.symptoms"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
