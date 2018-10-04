# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime
from .. import calculation as calc

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [("draft", "Draft"), ("moved", "Moved")]
PICKING_TYPE = [("in", "IN"), ("internal", "Internal"), ("out", "OUT")]

PICKING_CATEGORY = [("stock_adjust", "Stock Adjustment"),
                    ("store_issue", "Store Issue"),
                    ("store_intake", "Store Intake"),
                    ("material_receipt", "Material Receipt"),
                    ("direct_material_receipt", "Direct Material Receipt"),
                    ("material_return", "Material Return"),
                    ("material_delivery", "Material Delivery"),
                    ("material_intake", "Material Intake"),
                    ("delivery_return", "Delivery Return"),
                    ("assert_capitalisation", "Assert Capitalisation")]

INCOMING_SHIPMENT_DETAIL_KEY =["product_id", "reference", "source_location_id",
                               "destination_location_id", "picking_type"]

INCOMING_SHIPMENT_KEY = ["person_id", "picking_category", "reference",
                         "source_location_id", "destination_location_id", "picking_type",
                         "purchase_order_id", "purchase_return_id", "sale_order_id",
                         "sale_return_id", "store_request_id", "store_return_id"]


# Stock Picking
class Picking(models.Model):
    _name = "hos.picking"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", default=CURRENT_DATE, required=True)

    person_id = fields.Many2one(comodel_name="hos.person", string="Partner", readonly=True)
    picking_detail = fields.One2many(comodel_name="hos.move", inverse_name="picking_id", string="Stock Move")
    picking_type = fields.Selection(selection=PICKING_TYPE, string="Picking Type", required=True)
    picking_category = fields.Selection(selection=PICKING_CATEGORY, string="Picking Category")

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
    purchase_return_id = fields.Many2one(comodel_name="purchase.return", string="Purchase Return")
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    sale_return_id = fields.Many2one(comodel_name="sale.return", string="Sale Return")

    reference = fields.Char(string="Reference", readonly=True)
    reason = fields.Text(string="Reason")
    back_order_id = fields.Many2one(comodel_name="hos.picking", string="Back Order")
    is_invoice_created = fields.Boolean(string="Create Invoice")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    def get_shipment_requested_quantity(self, requested, actual):
        requested_quantity = 0

        if self.picking_category in ["store_issue", "store_intake", "material_receipt"]:
            requested_quantity = requested - actual

        return requested_quantity

    def generate_picking_detail(self):
        picking_detail = []

        recs = self.picking_detail
        for rec in recs:

            temp_move_detail = rec.copy_data()[0]
            move = calc.dictionary_reset(temp_move_detail, INCOMING_SHIPMENT_DETAIL_KEY)
            requested_quantity = self.get_shipment_requested_quantity(rec.requested_quantity, rec.quantity)

            if requested_quantity:
                move["requested_quantity"] = requested_quantity
                picking_detail.append((0, 0, move))

        return picking_detail

    def generate_incoming_shipment(self):
        picking_detail = self.generate_picking_detail()

        if picking_detail:

            temp_picking = self.copy_data()[0]
            picking = calc.dictionary_reset(temp_picking, INCOMING_SHIPMENT_KEY)
            picking["picking_detail"] = picking_detail
            picking["back_order_id"] = self.id

            self.env["hos.picking"].create(picking)

    def get_order_detail(self, product_id):
        order_id = None
        picking = self.picking_category

        if picking == "material_receipt":
            order_id = self.env["purchase.detail"].search([("product_id", "=", product_id),
                                                           ("order_id", "=", self.purchase_order_id.id)])
        elif picking == "material_return":
            order_id = self.env["purchase.return.detail"].search([("product_id", "=", product_id),
                                                                  ("return_id", "=", self.purchase_return_id.id)])
        elif picking == "material_delivery":
            order_id = self.env["sale.detail"].search([("product_id", "=", product_id),
                                                       ("order_id", "=", self.sale_order_id.id)])
        elif picking == "material_intake":
            order_id = self.env["sale.return.detail"].search([("product_id", "=", product_id),
                                                              ("return_id", "=", self.sale_return_id.id)])

        return order_id

    def get_unit_price(self, product_id):
        unit_price = 0

        order_id = self.get_order_detail(product_id)
        if order_id:
           unit_price = order_id.unit_price

        return unit_price

    def get_tax(self, product_id):
        tax_id = self.env.user.company_id.tax_id.id

        order_id = self.get_order_detail(product_id)
        if order_id:
            tax_id = order_id.tax_id.id

        return tax_id

    def get_discount(self, product_id):
        discount = 0

        order_id = self.get_order_detail(product_id)
        if order_id:
            discount = order_id.discount

        return discount

    def get_invoice_type(self):
        invoice_type = None
        category = self.picking_category

        if category == "material_receipt":
            invoice_type = "purchase_bill"
        elif category == "direct_material_receipt":
            invoice_type = "direct_purchase_bill"
        elif category == "material_return":
            invoice_type = "purchase_return_bill"
        elif category == "material_delivery":
            invoice_type = "sale_bill"
        elif category == "material_intake":
            invoice_type = "sale_return_bill"

        return invoice_type

    def generate_invoice_detail(self):
        invoice_detail = []
        recs = self.picking_detail

        for rec in recs:
            if rec.quantity > 0:
                data = {"product_id": rec.product_id.id,
                        "quantity": rec.quantity,
                        "unit_price": self.get_unit_price(rec.product_id.id),
                        "discount": self.get_discount(rec.product_id.id),
                        "tax_id": self.get_tax(rec.product_id.id)}

                invoice_detail.append((0, 0, data))

        return invoice_detail

    def generate_invoice(self):
        invoice_detail = self.generate_invoice_detail()

        data = {"date": CURRENT_DATE,
                "person_id": self.person_id.id,
                "reference": self.name,
                "invoice_detail": invoice_detail,
                "invoice_type": self.get_invoice_type(),
                "purchase_order_id": self.purchase_order_id.id,
                "purchase_return_id": self.purchase_return_id.id,
                "sale_order_id": self.sale_order_id.id,
                "sale_return_id": self.sale_return_id.id,
                "picking_id": self.id}

        invoice_id = self.env["hos.invoice"].create(data)
        invoice_id.total_calculation()

        self.write({"is_invoice_created": True})

    @api.multi
    def trigger_move(self):
        msg = "Stock Picked by {0} on {1}"
        writter = msg.format(self.env.user.name, CURRENT_TIME)
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

        msg = "Stock Picked reverted by {0} on {1}"
        writter = msg.format(self.env.user.name, CURRENT_TIME)
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
