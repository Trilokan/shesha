# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

PROGRESS_INFO = [('draft', 'Draft'), ('generated', 'Generated')]
PAY_TYPE = [('allowance', 'Allowance'), ('deduction', 'Deduction')]


# Pay Update
class HRPayWiz(models.TransientModel):
    _name = "hr.pay.wizard"

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee",
                                  default=lambda self: self.env.context.get('employee_id', False))
    basic = fields.Float(string="Basic",
                         default=lambda self: self.env.context.get('basic', False))
    structure_id = fields.Many2one(comodel_name="salary.structure", string="Salary Structure",
                                   default=lambda self: self.env.context.get('structure_id', False))

    def trigger_pay_update(self):
        writter = self.env["hr.employee"].search([("user_id", "=", self.env.user.id)])

        record = self.env["hr.pay"].search([("employee_id", "=", self.employee_id.id)])
        record.write({"basic": self.basic,
                      "structure_id": self.structure_id.id,
                      "writter": writter.id})
