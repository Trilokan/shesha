# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Operation(models.Model):
    _name = "hos.operation"

    name = ""
    date = ""
    patient_id = ""
    doctor_id = ""
    operation_id = ""

    employee_ids = ""
    progress = ""
    duration = ""
    from_time = ""
    till_time = ""
    comment = ""

    attachment_detail = ""
    attachment_procedure = ""
    payment_status = ""



