# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime


PROGRESS_INFO = [("draft", "Draft"), ("moved", "Moved")]
PICKING_TYPE = [("in", "IN"), ("internal", "Internal"), ("out", "OUT")]


# Batch Move
class BatchMove(models.Model):
    _name = "batch.move"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)

    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       required=True)

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    reference = fields.Char(string="Reference", readonly=True)
    batch_id = fields.Many2one(comodel_name="hos.batch", string="Stock Picking", required=True)
    quantity = fields.Float(string="Quantity", default=0, required=True)

    source_location_id = fields.Many2one(comodel_name="product.location",
                                         string="Source Location",
                                         default=lambda self: self.env.context.get("source_location_id", False),
                                         required=True)

    destination_location_id = fields.Many2one(comodel_name="product.location",
                                              string="Destination location",
                                              default=lambda self: self.env.context.get("destination_location_id", False),
                                              required=True)

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

