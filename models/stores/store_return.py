# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime


PROGRESS_INFO = [("draft", "Draft"),
                 ("confirmed", "Confirmed"),
                 ("approved", "Approved"),
                 ("cancelled", "Cancelled")]


# Store Return
class StoreReturn(models.Model):
    _name = "store.return"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)

    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       readonly=True)

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    department_id = fields.Many2one(comodel_name="hr.department",
                                    string="Department",
                                    required=True)

    return_detail = fields.One2many(comodel_name="store.return.detail",
                                    inverse_name="return_id",
                                    string="Return Detail")

    returned_by = fields.Many2one(comodel_name="hos.person",
                                  string="Returned By",
                                  default=lambda self: self.env.user.person_id.id,
                                  readonly=True)

    approved_by = fields.Many2one(comodel_name="hos.person",
                                  string="Approved By",
                                  readonly=True)

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    @api.multi
    def check_quantity(self):
        recs = self.env["store.return.detail"].search([("return_id", "=", self.id),
                                                       ("quantity", ">", 0)])

        if not recs:
            raise exceptions.ValidationError("Error! No Products Found")

    @api.multi
    def trigger_confirm(self):
        self.check_quantity()

        returned_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "Store Returned by {0} on {1}".format(returned_by.name,
                                                        datetime.now().strftime("%d-%m-%Y %H:%M"))

        self.write({"progress": "confirmed",
                    "returned_by": returned_by.id,
                    "writter": writter})

    @api.multi
    def trigger_cancel(self):
        cancelled_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "Store Return cancelled by {0} on {1}".format(cancelled_by.name,
                                                                datetime.now().strftime("%d-%m-%Y %H:%M"))

        self.write({"progress": "cancelled",
                    "writter": writter})

    @api.multi
    def trigger_approve(self):
        self.check_quantity()

        approved_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "Store Return approved by {0} on {1}".format(approved_by.name,
                                                               datetime.now().strftime("%d-%m-%Y %H:%M"))

        self.create_issue(writter)
        self.write({"progress": "approved",
                    "approved_by": approved_by.id,
                    "writter": writter})

    @api.multi
    def create_issue(self, writter):

        picking_detail = []
        recs = self.return_detail

        for rec in recs:
            if rec.quantity > 0:
                picking_detail.append((0, 0, {"reference": self.name,
                                              "product_id": rec.product_id.id,
                                              "requested_quantity": rec.quantity,
                                              "picking_type": "internal",
                                              "source_location_id": self.env.user.location_id.id,
                                              "destination_location_id": self.env.user.company_id.location_store_id.id}))

        data = {"reference": self.name,
                "picking_type": "internal",
                "picking_category": "store_intake",
                "picking_detail": picking_detail,
                "source_location_id": self.env.user.location_id.id,
                "destination_location_id": self.env.user.company_id.location_store_id.id,
                "store_return_id": self.id,
                "writter": writter}

        self.env["hos.picking"].create(data)

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)

        return super(StoreReturn, self).create(vals)


class StoreReturnDetail(models.Model):
    _name = "store.return.detail"

    product_id = fields.Many2one(comodel_name="hos.product", string="Product", required=True)
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", related="product_id.uom_id")
    quantity = fields.Float(string="Quantity", required=True)
    return_id = fields.Many2one(comodel_name="store.return", string="Store Return")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", related="return_id.progress")

    _sql_constraints = [('unique_return_detail', 'unique (product_id, return_id)',
                         'Error! Product should not be repeated')]
