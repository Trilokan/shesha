# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime

# Purchase Indent
PROGRESS_INFO = [('draft', 'Draft'),
                 ('approved', 'Approved'),
                 ('cancelled', 'Cancelled')]


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "mail.thread"

    name = fields.Char(string='Name', readonly=True)
    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       readonly=True)
    vendor_id = fields.Many2one(comodel_name="hos.person", string="Vendor", readonly=True)
    indent_id = fields.Many2one(comodel_name="purchase.indent", string="Purchase Indent", readonly=True)
    quote_id = fields.Many2one(comodel_name="purchase.quote", string="Quotation", readonly=True)
    vendor_ref = fields.Char(string="Vendor Ref")
    processed_by = fields.Many2one(comodel_name="hos.person", string="Processed By", readonly=True)
    processed_on = fields.Date(string='Processed On', readonly=True)
    order_detail = fields.One2many(comodel_name='purchase.detail',
                                   inverse_name='order_id',
                                   string='Order Detail')
    progress = fields.Selection(PROGRESS_INFO, default='draft', string='Progress')
    comment = fields.Text(string='Comment')

    discounted_amount = fields.Float(string='Discounted Amount', readonly=True, help='Amount after discount')
    taxed_amount = fields.Float(string='Taxed Amount', readonly=True, help='Tax after discounted amount')
    untaxed_amount = fields.Float(string='Untaxed Amount', readonly=True)
    sgst = fields.Float(string='SGST', readonly=True)
    cgst = fields.Float(string='CGST', readonly=True)
    igst = fields.Float(string='IGST', readonly=True)

    sub_total_amount = fields.Float(string='Sub Total', readonly=True)
    discount_amount = fields.Float(string='Discount Amount', readonly=True, help='Discount value')
    total_amount = fields.Float(string='Total', readonly=True)
    tax_amount = fields.Float(string='Tax Amount', readonly=True, help='Tax value')
    round_off_amount = fields.Float(string='Round-Off', readonly=True)
    grand_total_amount = fields.Float(string='Grand Total', readonly=True)

    expected_delivery = fields.Char(string='Expected Delivery')
    freight = fields.Char(string='Freight')
    payment = fields.Char(string='Payment')
    insurance = fields.Char(string='Insurance')
    certificate = fields.Char(string='Certificate')
    warranty = fields.Char(string='Warranty')

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    writter = fields.Text(string="Writter", track_visibility='always')

    @api.multi
    def total_calculation(self):
        recs = self.order_detail

        if not recs:
            raise exceptions.ValidationError("Error! Bill details not found")

        for rec in recs:
            rec.detail_calculation()

        discount_amount = discounted_amount = tax_amount = untaxed_amount = taxed_amount \
            = cgst = sgst = igst = sub_total_amount = 0

        for rec in recs:
            discount_amount = discount_amount + rec.discount_amount
            discounted_amount = discounted_amount + rec.discounted_amount
            tax_amount = tax_amount + rec.tax_amount
            untaxed_amount = untaxed_amount + rec.untaxed_amount
            taxed_amount = taxed_amount + rec.taxed_amount
            cgst = cgst + rec.cgst
            sgst = sgst + rec.sgst
            igst = igst + rec.igst
            sub_total_amount = sub_total_amount + rec.total_amount

        total_amount = sub_total_amount - discount_amount
        grand_total_amount = round(total_amount + tax_amount)
        round_off_amount = round(total_amount + tax_amount) - (total_amount + tax_amount)

        self.write({"discount_amount": discount_amount,
                    "discounted_amount": discounted_amount,
                    "tax_amount": tax_amount,
                    "untaxed_amount": untaxed_amount,
                    "taxed_amount": taxed_amount,
                    "cgst": cgst,
                    "sgst": sgst,
                    "igst": igst,
                    "sub_total_amount": sub_total_amount,
                    "total_amount": total_amount,
                    "grand_total_amount": grand_total_amount,
                    "round_off_amount": round_off_amount})

    def trigger_grn(self):
        data = {}

        hos_move = []
        recs = self.order_detail
        for rec in recs:
            if (rec.accepted_quantity > 0) and (rec.unit_price > 0):
                hos_move.append((0, 0, {"reference": self.name,
                                        "source_location_id": self.env.user.company_id.location_purchase_id.id,
                                        "destination_location_id": self.env.user.company_id.location_store_id.id,
                                        "picking_type": "in",
                                        "product_id": rec.product_id.id,
                                        "requested_quantity": rec.accepted_quantity}))

        if hos_move:
            data["person_id"] = self.vendor_id.id
            data["reference"] = self.name
            data["picking_detail"] = hos_move
            data["picking_type"] = 'in'
            data["date"] = datetime.now().strftime("%Y-%m-%d")
            data["purchase_order_id"] = self.id
            data["source_location_id"] = self.env.user.company_id.location_purchase_id.id
            data["destination_location_id"] = self.env.user.company_id.location_store_id.id
            data["picking_category"] = "material_receipt"
            picking_id = self.env["hos.picking"].create(data)
            return True
        return False

    @api.multi
    def trigger_po_approve(self):
        self.total_calculation()

        if not self.trigger_grn():
            raise exceptions.ValidationError("Error! Please check Product lines")

        writter = "PO approved by {0}".format(self.env.user.name)
        self.write({"progress": "approved", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        person_id = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "PO cancelled by {0}".format(person_id.name)

        self.write({"progress": "cancelled", "writter": writter})

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(PurchaseOrder, self).create(vals)
