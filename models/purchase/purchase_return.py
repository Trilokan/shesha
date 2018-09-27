# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime
from .. import calculation

# Purchase Indent
PROGRESS_INFO = [('draft', 'Draft'),
                 ('approved', 'Approved'),
                 ('cancelled', 'Cancelled')]


class PurchaseReturn(models.Model):
    _name = "purchase.return"
    _inherit = "mail.thread"

    name = fields.Char(string='Name', readonly=True)
    date = fields.Date(string="Date",
                       default=datetime.now().strftime("%Y-%m-%d"),
                       required=True)
    vendor_id = fields.Many2one(comodel_name="hos.person", string="Vendor", required=True)
    processed_by = fields.Many2one(comodel_name="hos.person", string="Processed By", readonly=True)
    processed_on = fields.Date(string='Processed On', readonly=True)
    return_detail = fields.One2many(comodel_name='purchase.return.detail',
                                    inverse_name='return_id',
                                    string='Return Detail')
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
        recs = self.return_detail

        if not recs:
            raise exceptions.ValidationError("Error! Bill details not found")

        for rec in recs:
            rec.detail_calculation()

        data = calculation.data_calculation(recs)
        self.write(data)

    def trigger_grn(self):
        data = {}

        hos_move = []
        recs = self.return_detail
        for rec in recs:
            if (rec.quantity > 0) and (rec.unit_price > 0):

                line_data = {"reference": self.name,
                             "source_location_id": self.env.user.company_id.location_store_id.id,
                             "destination_location_id": self.env.user.company_id.location_purchase_id.id,
                             "picking_type": "out",
                             "product_id": rec.product_id.id,
                             "requested_quantity": rec.quantity}

                hos_move.append((0, 0, line_data))

        if hos_move:
            data["person_id"] = self.vendor_id.id
            data["reference"] = self.name
            data["picking_detail"] = hos_move
            data["picking_type"] = 'out'
            data["date"] = datetime.now().strftime("%Y-%m-%d")
            data["purchase_return_id"] = self.id
            data["source_location_id"] = self.env.user.company_id.location_store_id.id
            data["destination_location_id"] = self.env.user.company_id.location_purchase_id.id
            data["picking_category"] = "material_return"
            picking_id = self.env["hos.picking"].create(data)
            return True
        return False

    @api.multi
    def trigger_purchase_return_approve(self):
        self.total_calculation()

        if not self.trigger_grn():
            raise exceptions.ValidationError("Error! Please check Product lines")

        writter = "Purchase Return approved by {0}".format(self.env.user.name)
        self.write({"progress": "approved", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        person_id = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "Purchase Return cancelled by {0}".format(person_id.name)

        self.write({"progress": "cancelled", "writter": writter})

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(PurchaseReturn, self).create(vals)
