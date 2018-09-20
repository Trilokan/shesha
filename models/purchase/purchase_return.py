# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime

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
                       readonly=True)
    vendor_id = fields.Many2one(comodel_name="hos.person", string="Vendor", readonly=True)
    processed_by = fields.Many2one(comodel_name="hos.person", string="Processed By", readonly=True)
    processed_on = fields.Date(string='Processed On', readonly=True)
    order_detail = fields.One2many(comodel_name='purchase.return.detail',
                                   inverse_name='return_id',
                                   string='Return Detail')
    progress = fields.Selection(PROGRESS_INFO, default='draft', string='Progress')
    comment = fields.Text(string='Comment')

    discount_amount = fields.Float(string='Discount Amount', readonly=True, help='Discount value')
    discounted_amount = fields.Float(string='Discounted Amount', readonly=True, help='Amount after discount')
    tax_amount = fields.Float(string='Tax Amount', readonly=True, help='Tax value')
    taxed_amount = fields.Float(string='Taxed Amount', readonly=True, help='Tax after discounted amount')
    untaxed_amount = fields.Float(string='Untaxed Amount', readonly=True)
    sgst = fields.Float(string='SGST', readonly=True)
    cgst = fields.Float(string='CGST', readonly=True)
    igst = fields.Float(string='IGST', readonly=True)
    gross_amount = fields.Float(string='Gross Amount', readonly=True)
    round_off_amount = fields.Float(string='Round-Off', readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    writter = fields.Text(string="Writter", track_visibility='always')


class PurchaseReturnDetail(models.Model):
    _name = 'purchase.return.detail'
    _description = 'Purchase Return Detail'

    vendor_id = fields.Many2one(comodel_name='hos.person', string='Vendor', readonly=True)
    product_id = fields.Many2one(comodel_name='hos.product', string='Product')
    uom_id = fields.Many2one(comodel_name='product.uom', string='UOM')
    requested_quantity = fields.Float(string='Requested Quantity', default=0, readonly=True)
    accepted_quantity = fields.Float(string='Accepted Quantity', default=0)
    unit_price = fields.Float(string='Unit Price', default=0)

    discount = fields.Float(string='Discount', default=0)
    discount_amount = fields.Float(string='Discount Amount', default=0, readonly=True)
    discounted_amount = fields.Float(string='Discounted Amount', readonly=True, help='Amount after discount')
    tax_id = fields.Many2one(comodel_name='product.tax', string='Tax', required=True)
    igst = fields.Float(string='IGST', default=0, readonly=True)
    cgst = fields.Float(string='CGST', default=0, readonly=True)
    sgst = fields.Float(string='SGST', default=0, readonly=True)
    tax_amount = fields.Float(string='Tax Amount', default=0, readonly=True)
    taxed_amount = fields.Float(string='Taxed Amount', default=0, readonly=True)
    untaxed_amount = fields.Float(string='Tax Amount', default=0, readonly=True)
    total_amount = fields.Float(string='Total', default=0, readonly=True)
    return_id = fields.Many2one(comodel_name='purchase.return', string='Purchase Return')
    progress = fields.Selection(PROGRESS_INFO, string='Progress', related='return_id.progress')

