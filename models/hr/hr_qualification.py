# -*- coding: utf-8 -*-

from odoo import models, fields

RESULT_INFO = [('pass', 'Pass'), ('fail', 'Fail'), ('discontinued', 'Discontinued')]


# Qualification
class HRQualification(models.Model):
    _name = "hr.qualification"

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    name = fields.Char(string="Name", required=True)
    institution = fields.Char(string="Institution", required=True)
    result = fields.Selection(selection=RESULT_INFO, string='Pass/Fail', required=True)
    enrollment_year = fields.Integer(string="Enrollment Year", required=True)
    completed_year = fields.Integer(string="Completed Year")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
