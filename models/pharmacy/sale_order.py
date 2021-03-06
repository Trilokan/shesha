# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime
from .. import calculation

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

# Sale Order
PROGRESS_INFO = [('draft', 'Draft'),
                 ('approved', 'Approved'),
                 ('cancelled', 'Cancelled')]


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "mail.thread"

    name = fields.Char(string='Name', readonly=True)
    date = fields.Date(string="Date", default=CURRENT_DATE, required=True)
    vendor_id = fields.Many2one(comodel_name="hos.person", string="Vendor", required=True)
    processed_by = fields.Many2one(comodel_name="hos.person", string="Processed By", readonly=True)
    processed_on = fields.Date(string='Processed On', readonly=True)
    order_detail = fields.One2many(comodel_name='sale.detail',
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

        data = calculation.data_calculation(recs)
        self.write(data)

    def get_batch_ids(self, batch):
        batch_ids = []
        for rec in batch:
            batch_ids.append(rec.id)

        return [(6, 0, batch_ids)]

    def trigger_grn(self):
        data = {}

        hos_move = []
        recs = self.order_detail
        for rec in recs:
            if (rec.quantity > 0) and (rec.unit_price > 0):

                print rec.batch_ids

                line_data = {"reference": self.name,
                             "source_location_id": self.env.user.company_id.location_pharmacy_id.id,
                             "destination_location_id": self.env.user.company_id.location_sale_id.id,
                             "picking_type": "out",
                             "product_id": rec.product_id.id,
                             "quantity": rec.quantity,
                             "batch_ids": self.get_batch_ids(rec.batch_ids)}

                hos_move.append((0, 0, line_data))

        if hos_move:
            data["person_id"] = self.vendor_id.id
            data["reference"] = self.name
            data["picking_detail"] = hos_move
            data["picking_type"] = 'out'
            data["date"] = datetime.now().strftime("%Y-%m-%d")
            data["sale_order_id"] = self.id
            data["source_location_id"] = self.env.user.company_id.location_pharmacy_id.id
            data["destination_location_id"] = self.env.user.company_id.location_sale_id.id
            data["picking_category"] = "material_delivery"
            picking_id = self.env["hos.picking"].create(data)
            return picking_id

        raise exceptions.ValidationError("Error! Please check Product lines")

    @api.multi
    def trigger_so_approve(self):
        self.total_calculation()

        picking_id = self.trigger_grn()
        picking_id.trigger_move()

        writter = "SO approved by {0}".format(self.env.user.name)
        self.write({"progress": "approved", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        person_id = self.env["hos.person"].search([("id", "=", self.env.user.person_id.id)])
        writter = "SO cancelled by {0}".format(person_id.name)

        self.write({"progress": "cancelled", "writter": writter})

    @api.model
    def create(self, vals):
        vals["name"] = self.env['ir.sequence'].next_by_code(self._name)
        return super(SaleOrder, self).create(vals)
