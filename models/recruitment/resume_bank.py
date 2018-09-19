# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

MARITAL_INFO = [('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')]
GENDER_INFO = [('male', 'Male'), ('female', 'Female')]


# Resume Bank
class ResumeBank(models.Model):
    _name = "resume.bank"
    _inherit = "hos.address"

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", default=datetime.now().strftime("%Y-%m-%d"))
    candidate_uid = fields.Char(string="Candidate ID", readonly=True)
    aadhar_card = fields.Char(string="Aadhar Card")
    image = fields.Binary(string="Image")
    small_image = fields.Binary(string="Image")
    very_small_image = fields.Binary(string="Image")

    # Contact Detail
    email = fields.Char(string="Email", required=True)
    mobile = fields.Char(string="Mobile", required=True)

    # Personal Detail
    age = fields.Integer(string="Age")
    dob = fields.Date(string="Date Of Birth")
    marital_status = fields.Selection(MARITAL_INFO, string="Marital Status")
    gender = fields.Selection(GENDER_INFO, string="Gender")

    # Order Detail
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    position_id = fields.Many2one(comodel_name="hr.designation", string="Position", required=True)

    # Education Details
    qualification_ids = fields.One2many(comodel_name="resume.qualification",
                                        inverse_name="resume_id",
                                        string="Qualification")
    experience_ids = fields.One2many(comodel_name="resume.experience",
                                     inverse_name="resume_id",
                                     string="Experience")

    attachment_ids = fields.Many2many(comodel_name="ir.attachment", string="Others")

    # Resume
    resume = fields.Binary(string="Resume")
    writter = fields.Text(string="Writter", track_visibility="always")
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.model
    def create(self, vals):
        vals["candidate_uid"] = self.env['ir.sequence'].sudo().next_by_code(self._name)
        vals["writter"] = "Resume Created by {0}".format(self.env.user.name)
        return super(ResumeBank, self).create(vals)
