# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime


PROGRESS_INFO = [("draft", "Draft"), ("moved", "Moved")]
PICKING_TYPE = [("in", "IN"), ("internal", "Internal"), ("out", "OUT")]


# Stock Move
class StockMove(models.Model):
    _name = "hos.move"
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

    picking_id = fields.Many2one(comodel_name="hos.picking", string="Stock Picking")

    picking_type = fields.Selection(selection=PICKING_TYPE,
                                    string="Picking Type",
                                    default=lambda self: self.env.context.get("picking_type", False),
                                    required=True)

    product_id = fields.Many2one(comodel_name="hos.product",
                                 string="Product",
                                 default=lambda self: self.env.context.get("product_id", False),
                                 required=True)

    uom_id = fields.Many2one(comodel_name="product.uom",
                             string="UOM",
                             related="product_id.uom_id")

    requested_quantity = fields.Float(string="Requested Quantity",
                                      default=0,
                                      readonly=True)

    quantity = fields.Float(string="Approved Quantity",
                            default=0,
                            required=True)

    source_location_id = fields.Many2one(comodel_name="product.location",
                                         string="Source Location",
                                         default=lambda self: self.env.context.get("source_location_id", False),
                                         required=True)

    destination_location_id = fields.Many2one(comodel_name="product.location",
                                              string="Destination location",
                                              default=lambda self: self.env.context.get("destination_location_id", False),
                                              required=True)

    assert_ids = fields.One2many(comodel_name="hos.asserts",
                                 inverse_name="move_id",
                                 string="Assert")

    is_batch = fields.Boolean(string="Batch", related="product_id.is_batch")
    dummy_batch_ids = fields.One2many(comodel_name="dum.batch", inverse_name="move_id", string="Batch")

    batch_ids = fields.Many2many(comodel_name="hos.batch", string="Batch")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    def get_balance_quantity(self, location):

        source = [("product_id", "=", self.product_id.id),
                  ("source_location_id", "=", location),
                  ("progress", "=", "moved")]

        destination = [("product_id", "=", self.product_id.id),
                       ("destination_location_id", "=", location),
                       ("progress", "=", "moved")]

        return self.env["hos.stock"].get_stock("hos.move", source, destination)

    def get_batch_quantity(self, batch_id, location):
        source = [("batch_id", "=", batch_id),
                  ("source_location_id", "=", location),
                  ("progress", "=", "moved")]

        destination = [("batch_id", "=", batch_id),
                       ("destination_location_id", "=", location),
                       ("progress", "=", "moved")]

        return self.env["hos.stock"].get_stock("batch.move", source, destination)

    def generate_assert(self):
        if self.picking_id.picking_category == 'assert_capitalisation':

            for qty in range(1, self.quantity + 1):
                data = {"date": self.date,
                        "product_id": self.product_id.id,
                        "move_id": self.id}

                self.env["hos.asserts"].create(data)

    def check_batch_quantity(self):
        if self.dummy_batch_ids:
            quantity = 0
            for rec in self.dummy_batch_ids:
                quantity = quantity + rec.quantity

            if self.quantity != quantity:
                raise exceptions.ValidationError("Error! Batch Quantity must be equal")

    def update_batch_movement(self):
        if self.dummy_batch_ids:
            for rec in self.dummy_batch_ids:
                batch_id = self.env["hos.batch"].search([("batch_no", "=", rec.batch_no),
                                                         ("product_id", "=", self.product_id.id)])

                data = {"batch_id": batch_id.id,
                        "source_location_id": self.source_location_id.id,
                        "destination_location_id": self.destination_location_id.id,
                        "quantity": rec.quantity,
                        "progress": "moved"}

                self.env["batch.move"].create(data)

    def quantity_calc(self, batch_qty, quantity):
        if batch_qty > quantity:
            move_quantity = quantity
        else:
            move_quantity = batch_qty

        return move_quantity

    def update_batch_movement_1(self):
        if self.batch_ids:
            location = self.source_location_id.id

            quantity = self.quantity
            for rec in self.batch_ids:
                batch_qty = self.get_batch_quantity(rec.id, location)

                if batch_qty > 0:

                    data = {"batch_id": rec.id,
                            "source_location_id": self.source_location_id.id,
                            "destination_location_id": self.destination_location_id.id,
                            "quantity": self.quantity_calc(batch_qty, quantity),
                            "progress": "moved"}

                    quantity = quantity - data["quantity"]
                    self.env["batch.move"].create(data)

            if quantity:
                raise exceptions.ValidationError("Error! Batch doesn't have enough stock to move")

    @api.multi
    def trigger_move(self):
        self.env["product.warehouse"].generate_warehouse(self.product_id.id, self.source_location_id.id)
        self.env["product.warehouse"].generate_warehouse(self.product_id.id, self.destination_location_id.id)

        writter = "Stock Moved by {0}".format(self.env.user.name)
        location = self.source_location_id.id
        quantity = self.get_balance_quantity(location)

        # Except Purchase
        if self.picking_type in ["internal", "out"]:
            if quantity < self.quantity:
                raise exceptions.ValidationError("Error! Product {0} has not enough stock to move".
                                                 format(self.product_id.name))

        self.generate_assert()
        self.check_batch_quantity()
        self.update_batch_movement()
        self.update_batch_movement_1()
        self.write({"progress": "moved", "writter": writter})

    @api.constrains("requested_quantity", "quantity")
    def check_requested_quantity(self):
        if self.picking_id.picking_category in ["store_issue",
                                                "assert_capitalisation",
                                                "material_receipt",
                                                "store_intake"]:
            if self.requested_quantity < self.quantity:
                error_msg = "Error! Approved/Store Quantity must be lower than requested quantity"
                raise exceptions.ValidationError(error_msg)

    @api.model
    def create(self, vals):
        code = "move.{0}".format(vals["picking_type"])
        vals["name"] = self.env['ir.sequence'].next_by_code(code)
        vals["writter"] = "Created by {0}".format(self.env.user.name)

        return super(StockMove, self).create(vals)
