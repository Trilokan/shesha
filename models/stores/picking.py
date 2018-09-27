# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime


PROGRESS_INFO = [("draft", "Draft"), ("moved", "Moved")]
PICKING_TYPE = [("in", "IN"), ("internal", "Internal"), ("out", "OUT")]

PICKING_CATEGORY = [("stock_adjust", "Stock Adjustment"),
                    ("store_issue", "Store Issue"),
                    ("store_intake", "Store Intake"),
                    ("material_receipt", "Material Receipt"),
                    ("direct_material_receipt", "Direct Material Receipt"),
                    ("material_return", "Material Return"),
                    ("material_delivery", "Material Delivery"),
                    ("delivery_return", "Delivery Return"),
                    ("assert_capitalisation", "Assert Capitalisation")]


# Stock Picking
class Picking(models.Model):
    _name = "hos.picking"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)

    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       required=True)

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    person_id = fields.Many2one(comodel_name="hos.person",
                                string="Partner",
                                readonly=True)

    picking_detail = fields.One2many(comodel_name="hos.move",
                                     inverse_name="picking_id",
                                     string="Stock Move")

    picking_type = fields.Selection(selection=PICKING_TYPE,
                                    string="Picking Type",
                                    required=True)

    picking_category = fields.Selection(selection=PICKING_CATEGORY,
                                        string="Picking Category")

    source_location_id = fields.Many2one(comodel_name="product.location",
                                         string="Source Location",
                                         default=lambda self: self._get_source_location_id(),
                                         required=True)

    destination_location_id = fields.Many2one(comodel_name="product.location",
                                              string="Destination location",
                                              default=lambda self: self._get_destination_location_id(),
                                              required=True)

    store_request_id = fields.Many2one(comodel_name="store.request", string="Store Request")
    store_return_id = fields.Many2one(comodel_name="store.return", string="Store Return")
    purchase_order_id = fields.Many2one(comodel_name="purchase.order", string="Purchase Order")
    # purchase_return_id = fields.Many2one(comodel_name="purchase.return", string="Purchase Return")
    # sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    # sale_return_id = fields.Many2one(comodel_name="sale.return", string="Sale Return")

    reference = fields.Char(string="Reference", readonly=True)

    reason = fields.Text(string="Reason")

    back_order_id = fields.Many2one(comodel_name="hos.picking", string="Back Order")

    is_invoice_created = fields.Boolean(string="Create Invoice")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    def get_purchase_data(self, rec):
        move_line = {}
        order_detail = self.env["purchase.detail"].search([("product_id", "=", rec.product_id.id),
                                                           ("order_id", "=", self.purchase_order_id.id)])

        if order_detail:
            move_line = {"unit_price": order_detail.unit_price,
                         "discount": order_detail.discount,
                         "tax_id": order_detail.tax_id.id}

        return move_line

    def generate_line(self):
        invoice_detail = []

        no_batch_recs = self.env["hos.move"].search([("picking_id", "=", self.id), ("is_batch", "=", False)])
        batch_recs = self.env["hos.move"].search([("split_id.picking_id", "=", self.id)])

        recs = no_batch_recs + batch_recs
        for rec in recs:
            if rec.quantity > 0:
                move_line = {"product_id": rec.product_id.id,
                             "quantity": rec.quantity,
                             "batch_id": rec.batch_id.id}

                if self.picking_category == "material_receipt":
                    move_line.update(self.get_purchase_data(rec))

                invoice_detail.append((0, 0, move_line))

        return invoice_detail

    def get_product_type(self):
        product_type = "not_batch"
        batch_recs = self.env["hos.move"].search([("split_id.picking_id", "=", self.id)])

        if batch_recs:
            product_type = "batch"

        return product_type

    @api.multi
    def trigger_create_purchase_invoice(self):
        data = {}
        invoice_detail = self.generate_line()

        if invoice_detail:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
            data["person_id"] = self.person_id.id
            data["reference"] = self.name
            data["invoice_detail"] = invoice_detail
            data["product_type"] = self.get_product_type()
            data["picking_id"] = self.id

        if self.picking_category == "material_receipt":
            data.update({"indent_id": self.purchase_order_id.indent_id.id,
                         "quote_id": self.purchase_order_id.quote_id.id,
                         "order_id": self.purchase_order_id.id,
                         "invoice_type": "purchase_bill"})

        if self.picking_category == "direct_material_receipt":
            data.update({"invoice_type": "direct_purchase_bill"})

        invoice_id = self.env["hos.invoice"].create(data)
        invoice_id.total_calculation()

        self.write({"is_invoice_created": True})

    def generate_incoming_shipment(self):
        data = {}

        hos_move = []
        recs = self.picking_detail
        for rec in recs:
            quantity = rec.requested_quantity - rec.quantity
            if quantity > 0:
                hos_move.append((0, 0, {"reference": rec.reference,
                                        "source_location_id": rec.source_location_id.id,
                                        "destination_location_id": rec.destination_location_id.id,
                                        "picking_type": rec.picking_type,
                                        "product_id": rec.product_id.id,
                                        "requested_quantity": quantity}))

        if hos_move:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
            data["person_id"] = self.person_id.id
            data["reference"] = self.reference
            data["picking_detail"] = hos_move
            data["picking_type"] = self.picking_type
            data["source_location_id"] = self.source_location_id.id
            data["destination_location_id"] = self.destination_location_id.id
            data["picking_category"] = self.picking_category
            data["back_order_id"] = self.id

            if self.purchase_order_id:
                data["purchase_order_id"] = self.purchase_order_id.id

            # if self.purchase_return_id:
            #     data["purchase_return_id"] = self.purchase_return_id.id
            #
            # if self.sale_order_id:
            #     data["sale_order_id"] = self.sale_order_id.id
            #
            # if self.sale_return_id:
            #     data["sale_return_id"] = self.sale_return_id.id
            #
            # if self.store_request_id:
            #     data["store_request_id"] = self.store_request_id.id
            #
            # if self.store_return_id:
            #     data["store_return_id"] = self.store_return_id.id

            self.env["hos.picking"].create(data)

    # Sale
    @api.multi
    def trigger_create_sale_invoice(self):
        data = {}

        invoice_detail = []
        recs = self.picking_detail
        for rec in recs:
            if rec.quantity > 0:
                order_detail = self.env["sale.detail"].search([("product_id", "=", rec.product_id.id),
                                                               ("order_id", "=", self.so_id.id)])

                invoice_detail.append((0, 0, {"product_id": rec.product_id.id,
                                              "quantity": rec.quantity,
                                              "unit_price": order_detail.unit_price,
                                              "discount": order_detail.discount,
                                              "tax_id": order_detail.tax_id.id}))

        if invoice_detail:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
            data["person_id"] = self.person_id.id
            data["reference"] = self.name
            data["invoice_detail"] = invoice_detail
            data["invoice_type"] = self.picking_category
            data["so_id"] = self.so_id.id
            data["picking_id"] = self.id

            invoice_id = self.env["hos.invoice"].create(data)
            invoice_id.total_calculation()

    @api.multi
    def trigger_move(self):
        writter = "Stock Picked by {0}".format(self.env.user.name)
        recs = self.picking_detail

        for rec in recs:
            rec.trigger_move()

        self.generate_incoming_shipment()
        self.write({"progress": "moved", "writter": writter})

    @api.multi
    def trigger_revert(self):
        # Invoice to be reverted

        invoice = self.env["hos.invoice"].search([("picking_id", "=", self.id),
                                                  ("progress", "in", ["draft", "approved"])])
        if invoice:
            raise exceptions.ValidationError("Error! Please cancel the invoice before Stock reverting")

        writter = "Stock Picked reverted by {0}".format(self.env.user.name)
        recs = self.picking_detail

        for rec in recs:
            rec.trigger_revert()

        self.write({"progress": "draft", "writter": writter})

    def _get_source_location_id(self):
        picking_category = self.env.context.get("default_picking_category", False)

        if picking_category in ['stock_adjust', 'direct_material_receipt']:
            return self.env.user.company_id.location_purchase_id.id
        elif picking_category == 'assert_capitalisation':
            return self.env.user.company_id.location_store_id.id

    def _get_destination_location_id(self):
        picking_category = self.env.context.get("default_picking_category", False)

        if picking_category in ['stock_adjust', 'direct_material_receipt']:
            return self.env.user.company_id.location_store_id.id
        elif picking_category == 'assert_capitalisation':
            return self.env.user.company_id.location_assert_id.id

    @api.model
    def create(self, vals):
        code = "picking.{0}".format(vals["picking_category"])
        vals["name"] = self.env['ir.sequence'].next_by_code(code)
        vals["writter"] = "Created by {0}".format(self.env.user.name)

        return super(Picking, self).create(vals)
