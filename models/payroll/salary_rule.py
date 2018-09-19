# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

PROGRESS_INFO = [('draft', 'Draft'), ('confirmed', 'Confirmed')]
RULE_TYPE = [('fixed', 'Fixed'), ('formula', 'Formula'), ('slab', 'Slab')]


# Salary Rule
class SalaryRule(models.Model):
    _name = "salary.rule"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True)
    code = fields.Many2one(comodel_name="salary.rule.code", string="Code", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    rule_type = fields.Selection(selection=RULE_TYPE, string="Type", required=True)
    fixed = fields.Float(string="Fixed Amount", default=0)
    formula = fields.Text(string="Formula")
    slab_ids = fields.One2many(comodel_name="salary.rule.slab", inverse_name="rule_id", string="Slab")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    @api.multi
    def trigger_confirm(self):
        if self.rule_type == 'fixed':
            if self.fixed <= 0:
                raise exceptions.ValidationError('Error! Fixed value is not found')

        elif self.rule_type == 'formula':
            if not self.formula:
                raise exceptions.ValidationError('Error! Formula is not found')

        elif self.rule_type == 'slab':
            if not self.slab_ids:
                raise exceptions.ValidationError('Error! Slab Value is not found')

        writter = "Salary Rule confirm by {0}".format(self.env.user.name)

        self.write({"progress": "confirmed", "writter": writter})

    @api.model
    def create(self, vals):
        vals["writter"] = "Salary Rule confirm by {0}".format(self.env.user.name)
        return super(SalaryRule, self).create(vals)
