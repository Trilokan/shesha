# -*- coding: utf-8 -*-

from odoo import models


# Stock
class Stock(models.Model):
    _name = "hos.stock"

    def get_stock(self, search_source, search_destination):
        source_ids = self.env["hos.move"].search(search_source)
        destination_ids = self.env["hos.move"].search(search_destination)

        quantity_in = quantity_out = 0

        for rec in destination_ids:
            quantity_in = quantity_in + rec.quantity

        for rec in source_ids:
            quantity_out = quantity_out + rec.quantity

        quantity = quantity_in - quantity_out

        return quantity
