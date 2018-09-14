# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime

BLOOD_GROUP = [('a+', 'A+'), ('b+', 'B+'), ('ab+', 'AB+'), ('o+', 'O+'),
               ('a-', 'A-'), ('b-', 'B-'), ('ab-', 'AB-'), ('o-', 'O-')]
GENDER = [('male', 'Male'), ('female', 'Female')]
MARITAL_STATUS = [('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')]


class Patient(models.Model):
    _name = "hos.patient"
    _inherit = "hos.address"

    date = fields.Date(string="Date", readonly=True, default=datetime.now().strftime("%Y-%m-%d"))
    name = fields.Char(string="Name", required=True)
    patient_uid = fields.Char(string="Patient ID", readonly=True)
    image = fields.Binary(string="Image")
    small_image = fields.Binary(string="Image")

    # Contact
    email = fields.Char(string="Email", required=True)
    contact_no = fields.Char(string="Contact No", required=True)
    alternate_contact = fields.Char(string="Alternate Contact")
    permanent_address = fields.Text(string="Permanent Address")

    # Professional
    work_position = fields.Char(string="Position")
    work_description = fields.Char(string="Company/Work Details")

    # Personnel Details
    dob = fields.Date(string="Date of Birth")
    gender = fields.Selection(selection=GENDER, string="Gender")
    age = fields.Char(string="Age", compute="_get_age")
    marital_status = fields.Selection(selection=MARITAL_STATUS, string="Marital Status")
    aadhar_card = fields.Char(string="Aadhar No")
    passport = fields.Char(string="Passport")
    driving_license = fields.Char(string="Driving Licence No")
    caste = fields.Char(string="Caste")
    religion_id = fields.Many2one(comodel_name="res.religion", string="Religion")
    physically_challenged = fields.Boolean(string="Physically Challenged")
    nationality_id = fields.Many2one(comodel_name="res.country")
    language_known_ids = fields.Many2many(comodel_name="hos.language", string="Language Known")
    family_member_ids = fields.One2many(comodel_name="hos.contact",
                                        inverse_name="patient_id",
                                        string="Family Members")

    # Medical Details
    blood_group = fields.Selection(selection=BLOOD_GROUP, string="Blood Group")
    allergic_towards = fields.Text(string="Allergic Towards")
    # treatment_detail = fields.One2many(comodel_name="hospital.treatment",
    #                                    inverse_name="patient_id",
    #                                    string="Treatment Details")
    report = fields.Html(string="Report")
    attachment_ids = fields.Many2many(comodel_name="ir.attachment", string="Attachment")
    person_id = fields.Many2one(comodel_name="hos.person", string="Partner")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True,
                                 default=lambda self: self.env.user.company_id.id)

    def _get_age(self):
        for record in self:
            if record.dob:
                today = datetime.now()
                age_obj = datetime.strptime(record.dob, "%Y-%m-%d")
                years = days = 0
                if today > age_obj:
                    total_days = (today - age_obj).days
                    years = int(total_days/365)

                record.age = "({0}) Years ({1}) Days".format(years, (total_days-years*365))

    def generate_person(self, vals):
        data = {"name": vals["name"],
                "contact_no": vals["contact_no"],
                "email": vals.get("email", None),
                "alternate_contact": vals.get("alternate_contact", None),
                "person_uid": vals["patient_uid"],
                "person_type": "patient"}

        person_id = self.env["hos.person"].create(data)
        vals["person_id"] = person_id.id

        return vals

    @api.model
    def create(self, vals):
        vals["patient_uid"] = self.env['ir.sequence'].next_by_code(self._name)
        vals = self.generate_person(vals)

        return vals

