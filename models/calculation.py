# -*- coding: utf-8 -*-


def purchase_calculation(unit_price, quantity, discount, tax, tax_state):
    price = unit_price * quantity

    discount_amount = price * float(discount)/100
    discounted_amount = price - discount_amount

    tax_amount = discounted_amount * float(tax)/100

    cgst = sgst = igst = 0
    if tax_state == 'Tamil Nadu':
        cgst = sgst = tax_amount / 2
    else:
        igst = tax_amount

    return {"cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "total_amount": price}
