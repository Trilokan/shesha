# -*- coding: utf-8 -*-

from odoo import fields, api, exceptions, _, models
from datetime import datetime, timedelta
from .. import calculation


PROGRESS_INFO = [('draft', 'Draft'), ('approved', 'approved'), ('cancel', 'Cancel')]
INVOICE_TYPE = [("direct_purchase_bill", "Direct Purchase Bill"),
                ("purchase_bill", "Purchase Bill"),
                ("purchase_return_bill", "Purchase Return Bill"),
                ("sale_bill", "Sale Bill"),
                ("sale_return_bill", "Sale Return Bill")]
PRODUCT_TYPE = [("batch", "Batch"), ("not_batch", "Not Batch")]


# Bills
class HospitalInvoice(models.Model):
    _name = "hos.invoice"
    _inherit = "mail.thread"

    date = fields.Date(srring="Date", default=datetime.now().strftime("%Y-%m-%d"), required=True)
    name = fields.Char(string="Name", readonly=True)
    person_id = fields.Many2one(comodel_name="hos.person", string="Partner", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 deafult=lambda self: self.env.user.company_id.id,
                                 string="Company",
                                 readdonly=True)
    indent_id = fields.Many2one(comodel_name="purchase.indent", string="Purchase Indent")
    quote_id = fields.Many2one(comodel_name="purchase.quote", string="Quotation")
    purchase_order_id = fields.Many2one(comodel_name="purchase.order", string="Purchase Order")
    purchase_return_id = fields.Many2one(comodel_name="purchase.return", string="Purchase Return")
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Purchase Order")
    sale_return_id = fields.Many2one(comodel_name="sale.return", string="Purchase Return")
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    picking_id = fields.Many2one(comodel_name="hos.picking", string="Material Receipt")
    reference = fields.Char(string="Reference")

    invoice_detail = fields.One2many(comodel_name="invoice.detail",
                                     inverse_name="invoice_id",
                                     string="Invoice detail")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    invoice_type = fields.Selection(selection=INVOICE_TYPE, string="Invoice Type", required=True)
    product_type = fields.Selection(selection=PRODUCT_TYPE, string="Product Type", required=True)

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

    writter = fields.Text(string="Writter", track_visibility='always')

    # payment_detail = fields.One2many(comodel_name="invoice.detail",
    #                                  inverse_name="invoice_id",
    #                                  string="Invoice detail")
    # Account_detail

    def get_period(self, date):
        period_id = self.env["period.period"].search([("from_date", "=>", date),
                                                      ("till_date", "<=", date),
                                                      ("progress", "=", "open")])

        if not period_id:
            raise exceptions.ValidationError("Error! Period is not open")

        return period_id

    def get_account(self, product_id):
        account_id = product_id.category_id.account_id

        if not account_id:
            raise exceptions.ValidationError("Error! Journal is not found")

        return account_id

    def get_description(self, name, value, price):
        description = "{0} {1} {2}".format(name, value, price)

        return description

    def get_journal(self, invoice_type):
        journal_id = None

        if invoice_type == "purchase_bill":
            pass
        elif invoice_type == "direct_purchase_bill":
            pass
        elif invoice_type == "purchase_return_bill":
            pass
        elif invoice_type == "sale_bill":
            pass
        elif invoice_type == "sale_return_bill":
            pass

        if not journal_id:
            raise exceptions.ValidationError("Error! Journal is not found")

        return journal_id

    def get_credit(self, invoice_type):
        credit = 0

        if invoice_type == "purchase_bill":
            pass
        elif invoice_type == "direct_purchase_bill":
            pass
        elif invoice_type == "purchase_return_bill":
            pass
        elif invoice_type == "sale_bill":
            pass
        elif invoice_type == "sale_return_bill":
            pass

        return credit

    def get_debit(self, invoice_type):
        debit = 0

        if invoice_type == "purchase_bill":
            pass
        elif invoice_type == "direct_purchase_bill":
            pass
        elif invoice_type == "purchase_return_bill":
            pass
        elif invoice_type == "sale_bill":
            pass
        elif invoice_type == "sale_return_bill":
            pass

        return debit

    def generate_journal_items(self):
        journal_item = []
        recs = self.invoice_detail

        for rec in recs:
            data = {"period_id": self.get_period(self.date),
                    "journal_id": self.get_journal(self.invoice_type),
                    "reference": self.name,
                    "progress": "posted",
                    "invoice_id": self.id,
                    "account_id": self.get_account(rec.product_id),
                    "description": self.get_description(rec.product_id.name, rec.quantity, rec.unit_price),
                    "credit": self.get_credit(self.invoice_type),
                    "debit": self.get_debit(self.invoice_type)}
            journal_item.append((0, 0, data))

    def generate_journal_entries(self):
        journal_item = self.generate_journal_items()

        if journal_item:
            data = {"period_id": self.get_period(self.date),
                    "journal_id": self.get_journal(self.invoice_type),
                    "reference": self.name,
                    "progress": "posted",
                    "journal_item": journal_item}

            self.env["journal.entries"].create(data)

    @api.multi
    def trigger_approve(self):
        self.total_calculation()

        writter = "Invoice approved by {0}".format(self.env.user.name)
        self.write({"progress": "approved", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        self.total_calculation()

        writter = "Invoice cancel by {0}".format(self.env.user.name)
        self.write({"progress": "cancel", "writter": writter})

    @api.multi
    def total_calculation(self):
        recs = self.invoice_detail

        if not recs:
            raise exceptions.ValidationError("Error! Bill details not found")

        for rec in recs:
            rec.detail_calculation()

        data = calculation.data_calculation(recs)
        self.write(data)

    @api.model
    def create(self, vals):
        code = "{0}.{1}".format("invoice", vals["invoice_type"])
        vals['name'] = self.env['ir.sequence'].next_by_code(code)
        vals['writter'] = self.env.user.name
        return super(HospitalInvoice, self).create(vals)


class InvoiceDetail(models.Model):
    _name = "invoice.detail"

    person_id = fields.Many2one(comodel_name="hos.person", string="Vendor", readonly=True)
    product_id = fields.Many2one(comodel_name="hos.product", string="Description", required=True)
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", related="product_id.uom_id")
    unit_price = fields.Float(string="Unit Price")
    quantity = fields.Float(string="Quantity", required=True)
    discount = fields.Float(string="Discount")
    tax_id = fields.Many2one(comodel_name="product.tax",
                             string="Tax",
                             default=lambda self: self.env.user.company_id.tax_id.id,
                             required=True)
    total_amount = fields.Float(string="Total Amount", readonly=True)
    cgst = fields.Float(string="CGST", readonly=True)
    sgst = fields.Float(string="SGST", readonly=True)
    igst = fields.Float(string="IGST", readonly=True)
    tax_amount = fields.Float(string="Tax Amount", readonly=True)
    discount_amount = fields.Float(string="Discount Amount", readonly=True)
    discounted_amount = fields.Float(string="Discounted Amount", readonly=True)
    untaxed_amount = fields.Float(string="Untaxed Value", readonly=True)
    taxed_amount = fields.Float(string="Taxed value", readonly=True)

    # Batch
    batch_id = fields.Many2one(comodel_name="hos.batch", string="Batch")
    manufactured_date = fields.Date(string="Manufacturing Date",
                                    related="batch_id.manufactured_date",
                                    readonly=True)
    expiry_date = fields.Date(string="Expiry Date",
                              related="batch_id.expiry_date",
                              readonly=True)
    mrp_rate = fields.Float(string="MRP",
                            related="batch_id.mrp_rate",
                            readonly=True)

    invoice_id = fields.Many2one(comodel_name="hos.invoice", string="Hospital Invoice")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", related="invoice_id.progress")

    @api.multi
    def detail_calculation(self):
        data = calculation.purchase_calculation(self.unit_price,
                                                self.quantity,
                                                self.discount,
                                                self.tax_id.rate,
                                                self.person_id.state_id.name)
        self.write(data)
