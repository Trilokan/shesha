# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime


PROGRESS_INFO = [("draft", "Draft"),
                 ("confirmed", "Confirmed"),
                 ("approved", "Approved"),
                 ("cancelled", "Cancelled")]


# Purchase Indent
class PurchaseIndent(models.Model):
    _name = "purchase.indent"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       readonly=True)
    requested_by = fields.Many2one(comodel_name="hos.person",
                                   default=lambda self: self.env.user.person_id.id,
                                   string="Requested By",
                                   readonly=True)
    approved_by = fields.Many2one(comodel_name="hos.person",
                                  string="Approved By",
                                  readonly=True)
    department_id = fields.Many2one(comodel_name="hr.department",
                                    string="Department",
                                    readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    indent_detail = fields.One2many(comodel_name="purchase.indent.detail",
                                    inverse_name="indent_id",
                                    string="Indent Detail")
    progress = fields.Selection(selection=PROGRESS_INFO,
                                string="Progress",
                                default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    # Smart Button
    po_count = fields.Integer(string="Purchase Order", compute="get_po_count")
    invoice_count = fields.Integer(string="Invoice", compute="get_invoice_count")
    mr_count = fields.Integer(string="Material Receipt", compute="get_mr_count")

    # Smart Button
    def get_po_count(self):
        po = self.env["purchase.order"].search_count([("indent_id", "=", self.id),
                                                      ("progress", "=", "approved")])
        return po

    def get_mr_count(self):
        mr = self.env["hos.picking"].search_count([("purchase_order_id.indent_id", "=", self.id),
                                                   ("progress", "=", "moved")])
        return mr

    def get_invoice_count(self):
        inv = self.env["hos.invoice"].search_count([("indent_id", "=", self.id),
                                                    ("progress", "=", "approved")])
        return inv

    def action_view_po(self):
        pass

    def action_view_mr(self):
        pass

    def action_view_invoice(self):
        pass

    @api.multi
    def check_quantity(self):
        recs = self.env["purchase.indent.detail"].search([("indent_id", "=", self.id), ("quantity", ">", 0)])

        if not recs:
            raise exceptions.ValidationError("Error! No Products Found")

    @api.multi
    def trigger_confirm(self):
        self.check_quantity()

        requested_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        employee_id = self.env["hr.employee"].search([("person_id", "=", self.env.user.person_id.id)])
        writter = "Purchase Indent by {0} on {1}".format(requested_by.name,
                                                         datetime.now().strftime("%d-%m-%Y %H:%M"))

        self.write({"progress": "confirmed",
                    "requested_by": requested_by.id,
                    "department_id": employee_id.department_id.id,
                    "writter": writter})

    @api.multi
    def trigger_cancel(self):
        cancelled_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "Purchase Indent cancelled by {0} on {1}".format(cancelled_by.name,
                                                                   datetime.now().strftime("%d-%m-%Y %H:%M"))

        self.write({"progress": "cancelled",
                    "writter": writter})

    def get_last_5_invoice_transaction(self, product_id):
        history = []
        recs = self.env["invoice.detail"].search([("product_id", "=", product_id),
                                                  ("invoice_id.invoice_type", "in", ["purchase_bill", "direct_purchase_bill"])],
                                                 limit=5,
                                                 order="id desc")

        for rec in recs:
            data = rec.copy_data()[0]
            data['vendor_id'] = data.pop('person_id')
            history.append((0, 0, data))

        return history

    @api.multi
    def create_quote(self, writter):

        quote_detail = []

        recs = self.env["purchase.indent.detail"].search([("quantity", ">", 0),
                                                          ("indent_id", "=", self.id)])

        for rec in recs:
            quote_detail.append((0, 0, {"product_id": rec.product_id.id,
                                        "quantity": rec.quantity,
                                        "purchase_history": self.get_last_5_invoice_transaction(rec.product_id.id)}))

        data = {"indent_id": self.id,
                "quote_detail": quote_detail,
                "writter": writter}

        self.env["purchase.quote"].create(data)

    @api.multi
    def trigger_approve(self):
        self.check_quantity()

        approved_by = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "Purchase indent approved by {0} on {1}".format(approved_by.name,
                                                                  datetime.now().strftime("%d-%m-%Y %H:%M"))

        self.create_quote(writter)
        self.write({"progress": "approved",
                    "approved_by": approved_by.id,
                    "writter": writter})

    @api.model
    def create(self, vals):
        employee_id = self.env["hr.employee"].search([("person_id", "=", self.env.user.person_id.id)])
        vals["department_id"] = employee_id.department_id.id
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)

        return super(PurchaseIndent, self).create(vals)


class PurchaseIndentDetail(models.Model):
    _name = "purchase.indent.detail"

    product_id = fields.Many2one(comodel_name="hos.product", string="Product", required=True)
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", related="product_id.uom_id")
    quantity = fields.Float(string="Quantity")
    indent_id = fields.Many2one(comodel_name="purchase.indent", string="Purchase Indent")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", related="indent_id.progress")

    _sql_constraints = [('unique_indent_detail', 'unique (product_id, indent_id)',
                         'Error! Product should not be repeated')]
