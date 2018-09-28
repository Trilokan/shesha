# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


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
    is_batch = fields.Boolean(string="Batch")
    min_stock = fields.Integer(string="Min Stock")
    max_stock = fields.Integer(string="Max Stock")

    # Smart Button
    indent_count = fields.Integer(string="Indent", compute="_get_indent_count")
    purchase_order_count = fields.Integer(string="Purchase Order", compute="_get_purchase_order_count")
    sale_order_count = fields.Integer(string="Sale Order", compute="_get_sale_order_count")
    incoming_shipment_count = fields.Integer(string="Incoming Shipment", compute="_get_incoming_shipment_count")
    invoice_count = fields.Integer(string="Invoice", compute="_get_invoice_count")
    batch_count = fields.Integer(string="Batch", compute="_get_batch_count")
    assert_count = fields.Integer(string="Assert", compute="_get_assert_count")

    company_id = fields.Many2one(comodel_name="res.company",
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)

    _sql_constraints = [('unique_code', 'unique (code)', 'Error! Product Code must be unique'),
                        ('unique_name', 'unique (name)', 'Error! Product must be unique')]

    # Smart Button
    def _get_indent_count(self):
        return 0

    def _get_purchase_order_count(self):
        return 0

    def _get_sale_order_count(self):
        return 0

    def _get_incoming_shipment_count(self):
        return 0

    def _get_invoice_count(self):
        return 0

    def _get_batch_count(self):
        return 0

    def _get_assert_count(self):
        pass

    @api.multi
    def action_view_indent(self):
        pass

    @api.multi
    def action_view_purchase_order(self):
        pass

    @api.multi
    def action_view_sale_order(self):
        pass

    @api.multi
    def action_view_incoming_shipment(self):
        pass

    @api.multi
    def action_view_invoice(self):
        pass

    @api.multi
    def action_view_batch(self):
        pass

    @api.multi
    def action_view_assert(self):
        pass

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

    def generate_warehouse(self, rec):
        location_store_id = self.env.user.company_id.location_store_id

        if not location_store_id:
            raise exceptions.ValidationError("Default Product Location is not set")

        self.env["product.warehouse"].generate_warehouse(rec.id, location_store_id.id)

    def _get_code(self, vals):
        group_id = self.env["product.group"].search([("id", "=", vals["group_id"])])
        sub_group_id = self.env["product.sub.group"].search([("id", "=", vals["sub_group_id"])])

        return "{0}/{1}".format(group_id.code, sub_group_id.code)

    @api.model
    def create(self, vals):
        code = self._get_code(vals)
        sequence = self.env["ir.sequence"].next_by_code(self._name)
        vals["code"] = "{0}/{1}".format(code, sequence)

        rec = super(Product, self).create(vals)
        self.generate_warehouse(rec)

        return rec
