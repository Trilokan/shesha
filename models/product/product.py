# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


# Product
class Product(models.Model):
    _name = "hos.product"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", readonly=True)
    group_id = fields.Many2one(comodel_name="product.group", string="Group", required=True)
    sub_group_id = fields.Many2one(comodel_name="product.sub.group", string="Sub Group", required=True)
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", required=True)
    category_id = fields.Many2one(comodel_name="product.category", string="Category", required=True)
    warehouse_ids = fields.One2many(comodel_name="product.warehouse",
                                    inverse_name="product_id",
                                    string="Warehouse",
                                    domain=lambda self: self._get_warehouse_ids(),
                                    readonly=True)
    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    min_stock = fields.Integer(string="Min Stock")
    max_stock = fields.Integer(string="Max Stock")
    is_batch = fields.Boolean(string="Batch")

    _sql_constraints = [('unique_code', 'unique (code)', 'Error! Product Code must be unique'),
                        ('unique_name', 'unique (name)', 'Error! Product must be unique')]

    def _get_warehouse_ids(self):
        location_left = self.env.user.company_id.location_left
        location_right = self.env.user.company_id.location_right

        domain = [('location_id.location_left', '>=', location_left),
                  ('location_id.location_right', '<=', location_right)]

        virtual_location = self.env["product.warehouse"].search(domain)

        return [("id", "not in", virtual_location.ids)]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|', ('name', '=', name), ('code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(['|', ('name', operator, name), ('code', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "[{0}] {1}".format(record.code, record.name)
            result.append((record.id, name))
        return result

    def _get_code(self, vals):
        group_id = self.env["product.group"].search([("id", "=", vals["group_id"])])
        sub_group_id = self.env["product.sub.group"].search([("id", "=", vals["sub_group_id"])])

        return "{0}/{1}".format(group_id.code, sub_group_id.code)

    def generate_warehouse(self, rec):
        location_store_id = self.env.user.company_id.location_store_id

        if not location_store_id:
            raise exceptions.ValidationError("Default Product Location is not set")

        self.env["product.warehouse"].create({"product_id": rec.id,
                                          "location_id": location_store_id.id})

    @api.model
    def create(self, vals):
        code = self._get_code(vals)
        sequence = self.env["ir.sequence"].next_by_code(self._name)
        vals["code"] = "{0}/{1}".format(code, sequence)

        rec = super(Product, self).create(vals)
        self.generate_warehouse(rec)

        return rec
