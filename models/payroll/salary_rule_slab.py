# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

SLAB_TYPE = [('fixed', 'Fixed'), ('formula', 'Formula')]


# Salary Rule Slab
class SalaryRuleSlab(models.Model):
    _name = "salary.rule.slab"
    _inherit = "mail.thread"

    range_from = fields.Float(string="Range From", required=True)
    range_till = fields.Float(string="Range Till", required=True)
    slab_input = fields.Text(string="Slab Input")
    slab_type = fields.Selection(selection=SLAB_TYPE, string="Slab Type")
    fixed = fields.Float(string="Fixed Amount")
    formula = fields.Text(string="Formula")
    rule_id = fields.Many2one(comodel_name="salary.rule", string="Salary Rule")
    writter = fields.Text(string="Writter", track_visibility='always')

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    @api.model
    def create(self, vals):
        vals["writter"] = "Salary Rule Slab created by {0}".format(self.env.user.name)
        return super(SalaryRuleSlab, self).create(vals)
