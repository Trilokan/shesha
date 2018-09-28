# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [("draft", "Draft"),
                 ("confirmed", "Confirmed"),
                 ("approved", "Approved"),
                 ("cancelled", "Cancelled")]


# Store Request
class StoreRequest(models.Model):
    _name = "store.request"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", default=CURRENT_DATE, readonly=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", required=True)

    requested_by = fields.Many2one(comodel_name="hos.person",
                                   string="Requested By",
                                   default=lambda self: self.env.user.person_id.id,
                                   readonly=True)

    approved_by = fields.Many2one(comodel_name="hos.person", string="Approved By", readonly=True)

    request_detail = fields.One2many(comodel_name="store.request.detail",
                                     inverse_name="request_id",
                                     string="Request Detail")

    # Smart Button
    issue_count = fields.Integer(string="Issue", compute="_get_issue_count")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    def _get_issue_count(self):
        return 0

    @api.multi
    def check_quantity(self):
        recs = self.env["store.request.detail"].search([("request_id", "=", self.id), ("quantity", ">", 0)])

        if not recs:
            raise exceptions.ValidationError("Error! No Products Found")

    @api.multi
    def trigger_confirm(self):
        self.check_quantity()

        requested_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        msg = "Store Requested by {0} on {1}"
        writter = msg.format(requested_by.name, CURRENT_TIME)

        self.write({"progress": "confirmed", "requested_by": requested_by.id, "writter": writter})

    @api.multi
    def trigger_cancel(self):
        cancelled_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        msg = "Store Request cancelled by {0} on {1}"
        writter = msg.format(cancelled_by.name, CURRENT_TIME)

        self.write({"progress": "cancelled", "writter": writter})

    @api.multi
    def trigger_approve(self):
        self.check_quantity()

        approved_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        msg = "Store Request approved by {0} on {1}"
        writter = msg.format(approved_by.name, CURRENT_TIME)

        self.create_issue(writter)
        self.write({"progress": "approved", "approved_by": approved_by.id, "writter": writter})

    @api.multi
    def create_issue(self, writter):

        picking_detail = []
        recs = self.request_detail

        for rec in recs:
            if rec.quantity > 0:
                picking_detail.append((0, 0, {"reference": self.name,
                                              "product_id": rec.product_id.id,
                                              "requested_quantity": rec.quantity,
                                              "picking_type": "internal",
                                              "source_location_id": self.env.user.company_id.location_store_id.id,
                                              "destination_location_id": self.env.user.location_id.id}))

        data = {"reference": self.name,
                "picking_type": "internal",
                "picking_category": "store_issue",
                "picking_detail": picking_detail,
                "source_location_id": self.env.user.company_id.location_store_id.id,
                "destination_location_id": self.env.user.location_id.id,
                "store_request_id": self.id,
                "writter": writter}

        self.env["hos.picking"].create(data)

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)

        return super(StoreRequest, self).create(vals)


class StoreRequestDetail(models.Model):
    _name = "store.request.detail"

    product_id = fields.Many2one(comodel_name="hos.product", string="Product", required=True)
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", related="product_id.uom_id")
    quantity = fields.Float(string="Quantity", required=True)
    request_id = fields.Many2one(comodel_name="store.request", string="Store Request")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", related="request_id.progress")

    _sql_constraints = [('unique_request_detail', 'unique (product_id, request_id)',
                         'Error! Product should not be repeated')]
