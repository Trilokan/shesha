# -*- coding: utf-8 -*-

from odoo import fields, models


# Contacts
class ResumeContact(models.Model):
    _name = "resume.contact"
    _inherit = "hos.address"

    resume_id = fields.Many2one(comodel_name="resume.bank", string="Resume Bank")


# Experience
class ResumeExperience(models.Model):
    _name = "resume.experience"

    resume_id = fields.Many2one(comodel_name="resume.bank", string="Resume Bank")
    name = fields.Char(string="Name", required=True)
    position = fields.Char(string="Position", required=True)
    total_years = fields.Float(string="Total Years", required=True)
    relieving_reason = fields.Text(string="Relieving Reason", required=True)


RESULT_INFO = [('pass', 'Pass'), ('fail', 'Fail'), ('discontinued', 'Discontinued')]


# Qualification
class ResumeQualification(models.Model):
    _name = "resume.qualification"

    resume_id = fields.Many2one(comodel_name="resume.bank", string="Resume Bank")
    name = fields.Char(string="Name", required=True)
    institution = fields.Char(string="Institution", required=True)
    result = fields.Selection(selection=RESULT_INFO, string='Pass/Fail', required=True)
    enrollment_year = fields.Integer(string="Enrollment Year", required=True)
    completed_year = fields.Integer(string="Completed Year")
