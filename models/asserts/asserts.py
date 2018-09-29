# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%d-%m-%Y %H:%M")

PROGRESS_INFO = [('draft', 'Draft'), ('confirmed', 'Confirmed')]


# Assert
class Assert(models.Model):
    _name = "hos.asserts"
    _inherit = "mail.thread"

    date = fields.Date(string="Date", default=CURRENT_DATE, required=True)
    name = fields.Char(string="Name", readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    move_id = fields.Many2one(comodel_name="hos.move", string="Move")

    # Manufacturing Details
    product_id = fields.Many2one(comodel_name="hos.product", string="Product", required=True)
    manufacturer = fields.Char(string="Manufacturer")
    manufactured_date = fields.Date(string="Date of Manufactured")
    expiry_date = fields.Date(string="Date of Expiry")
    serial_no = fields.Char(string="Serial No")
    model_no = fields.Char(string="Manufacturer")
    warranty_date = fields.Date(string="Warranty Date")

    # Seller Details
    vendor_id = fields.Many2one(comodel_name="hos.person", string="Vendor")
    purchase_date = fields.Date(string="Date of Purchase")
    # vendor_contact = ""
    # vendor_address = ""

    # Service Details
    service_id = fields.Many2one(comodel_name="hos.person", string="Service")
    # service_contact = ""
    # service_address = ""
    service_details = fields.One2many(comodel_name="asserts.service",
                                      inverse_name="assert_id",
                                      string="Service Details")
    reminder_details = fields.One2many(comodel_name="asserts.reminder",
                                       inverse_name="assert_id",
                                       string="Reminder Details")

    # Accounting Details
    account_id = fields.Many2one(comodel_name="hos.account", string="Account")
    depreciation_percentage = fields.Float(string="Depreciation Percentage")
    responsible_id = fields.Many2one(comodel_name="hos.person", string="Responsible Person")
    is_working = fields.Boolean(string="Is Working")
    is_condem = fields.Boolean(string="Is Condemed")
    attachment = fields.Many2many(comodel_name="ir.attachment", string="Attachment")

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")

    _sql_constraints = [('unique_name', 'unique (name)', 'Error! Assert must be unique')]

    @api.multi
    def trigger_confirm(self):
        msg = "Asserts Confirmed by {0} on {1}"
        writter = msg.format(self.env.user.name, CURRENT_TIME)

        self.write({"progress": "confirmed", "writter": writter})

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code(self._name)

        msg = "Assert Created by {0} on {1}"
        vals["writter"] = msg.format(self.env.user.name, CURRENT_TIME)
        return super(Assert, self).create(vals)
