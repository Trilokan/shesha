# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions


# Leave Configuration
class LeaveConfigurationMonth(models.Model):
    _name = "leave.configuration"
    _rec_name = "leave_type_id"

    leave_type_id = fields.Many2one(comodel_name="leave.type", string="Leave Type", required=True)
    leave_credit = fields.Float(string="Credit Days", required=True)
    leave_level_id = fields.Many2one(comodel_name="leave.level", string="Leave Level", required=True)
    leave_order = fields.Integer(string="Order Sequence", required=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)




