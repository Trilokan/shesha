# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

PROGRESS_INFO = [('draft', 'Draft'), ('confirmed', 'Confirmed')]


# HR Pay
class HRPay(models.Model):
    _name = "hr.pay"
    _inherit = "mail.thread"
    _rec_name = "employee_id"

    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="Employee",
                                  required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    basic = fields.Float(string="Basic", required=True)
    structure_id = fields.Many2one(comodel_name="salary.structure",
                                   string="Salary Structure",
                                   required=True)

    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    _sql_constraints = [('name_uniq', 'unique(employee_id)', 'Payscale is already configured')]

    def trigger_confirm(self):
        writter = "Pay detail for {0} with basic {1} Created by {2}".format(self.employee_id.name,
                                                                            self.basic,
                                                                            self.env.user.name)
        self.write({"progress": "confirmed", "writter": writter})

    @api.model
    def create(self, vals):
        employee_id = self.env["hr.employee"].search([("id", "=", vals["employee_id"])])
        writter = "Pay detail for {0} with basic {1} Created by {2}"
        vals["writter"] = writter.format(employee_id.name, vals["basic"], self.env.user.name)

        return super(HRPay, self).create(vals)
