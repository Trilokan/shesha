# -*- coding: utf-8 -*-

from odoo import models, fields, api

PROGRESS_INFO = [('draft', 'Draft'), ('confirmed', 'Confirmed')]


# Assert Service
class AssertsService(models.Model):
    _name = "asserts.service"
    _inherit = "mail.thread"

    date = fields.Date(string="Date")
    assert_id = fields.Many2one(comodel_name="hos.asserts", string="Assert")
    person_id = fields.Many2one(comodel_name="hos.person", string="Service")
    description = fields.Text(string="Description")
    attachment = fields.Many2many(comodel_name="ir.attachment", string="Attachment")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")

    @api.model
    def create(self, vals):
        vals["writter"] = "Assert Service Created by {0}".format(self.env.user.name)
        return super(AssertsService, self).create(vals)
