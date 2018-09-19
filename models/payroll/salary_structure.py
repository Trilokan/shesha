# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions

PROGRESS_INFO = [('draft', 'Draft'), ('confirmed', 'Confirmed')]
PAY_TYPE = [('allowance', 'Allowance'), ('deduction', 'Deduction')]


# Salary Structure
class SalaryStructure(models.Model):
    _name = "salary.structure"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    detail_ids = fields.One2many(comodel_name="salary.structure.detail",
                                 inverse_name="structure_id",
                                 string="Salary Structure Detail")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility='always')

    @api.multi
    def trigger_confirm(self):
        if not self.detail_ids:
            raise exceptions.ValidationError("Error! Salary Rules Not found")

        writter = "Salary Structure is confirmed by {0}".format(self.env.user.name)
        self.write({"progress": "confirmed", "writter": writter})

    @api.model
    def create(self, vals):
        vals["writter"] = "Salary Structure is confirmed by {0}".format(self.env.user.name)
        return super(SalaryStructure, self).create(vals)


class SalaryStructureDetail(models.Model):
    _name = "salary.structure.detail"

    rule_id = fields.Many2one(comodel_name="salary.rule", string="Salary Rule", required=True)
    code = fields.Many2one(comodel_name="salary.rule.code", string="Code", related="rule_id.code")
    sequence = fields.Integer(string="Sequence")
    is_need = fields.Boolean(string="Is Need")
    structure_id = fields.Many2one(comodel_name="salary.structure", string="Salary Structure")
    pay_type = fields.Selection(PAY_TYPE, string='Pay Type', required=True)
    progress = fields.Selection(PROGRESS_INFO, string='Progress', related='structure_id.progress')

    _sql_constraints = [('rule_uniq', 'unique(rule_id, structure_id)', 'Salary Structure should not duplicated')]
