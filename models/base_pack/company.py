# -*- coding: utf-8 -*-

from odoo import models, fields


class HospitalCompany(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    state_id = fields.Many2one(comodel_name="res.country.state",
                               string="State",
                               default=lambda self: self._get_state())
    email = fields.Char(string="E-mail")
    contact_no = fields.Char(string="Contact No")

    # Tax
    tax_id = fields.Many2one(comodel_name="product.tax", string="Tax")

    # Leave
    leave_lop_id = fields.Many2one(comodel_name="leave.account", string="Loss Of Pay")
    leave_credit_id = fields.Many2one(comodel_name="leave.account", string="Leave Credit")
    leave_debit_id = fields.Many2one(comodel_name="leave.account", string="Leave Debit")

    # Stock
    location_store_id = fields.Many2one(comodel_name="product.location", string="Store Location")
    location_pharmacy_id = fields.Many2one(comodel_name="product.location", string="Pharmacy Location")
    location_purchase_id = fields.Many2one(comodel_name="product.location", string="Purchase Location")
    location_sale_id = fields.Many2one(comodel_name="product.location", string="Sale Location")
    location_assert_id = fields.Many2one(comodel_name="hos.asserts", string="Assert Location")
    location_left = fields.Integer(string="Location Left")
    location_right = fields.Integer(string="Location Right")

    # Account
    sundry_creditor_id = fields.Many2one(comodel_name="hos.account", string="Sundry Creditor")
    sundry_debtor_id = fields.Many2one(comodel_name="hos.account", string="Sundry Debitor")

    # Template
    template_appointment_order = fields.Html(string="Appointment Order Template")
    template_attendance = fields.Html(string="Monthly Attendance Report")

    def _get_state(self):
        state_id = self.env["res.country.state"].search([("name", "=", "Tamil Nadu")])
        return state_id.id
