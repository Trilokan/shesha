# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from .. import calculation


PROGRESS_INFO = [('draft', 'Draft'),
                 ('approved', 'Approved'),
                 ('cancelled', 'Cancelled')]


class PurchaseReturnDetail(models.Model):
    _name = 'purchase.return.detail'
    _description = 'Purchase Order Detail'

    return_id = fields.Many2one(comodel_name='purchase.return', string='Purchase Return')
    vendor_id = fields.Many2one(comodel_name='hos.person', string='Vendor', readonly=True)
    product_id = fields.Many2one(comodel_name='hos.product', string='Product')
    uom_id = fields.Many2one(comodel_name='product.uom', string='UOM', related='product_id.uom_id')
    returned_quantity = fields.Float(string='Returned Quantity', default=0)
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
    progress = fields.Selection(PROGRESS_INFO, string='Progress', related='return_id.progress')

    @api.multi
    def detail_calculation(self):
        data = calculation.purchase_calculation(self.unit_price,
                                                self.returned_quantity,
                                                self.discount,
                                                self.tax_id.rate,
                                                self.vendor_id.state_id.name)
        self.write(data)

