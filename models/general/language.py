# -*- coding: utf-8 -*-

from odoo import models, fields


# Language
class Language(models.Model):
    _name = "hos.language"

    name = fields.Char(string="Language", required=True)

