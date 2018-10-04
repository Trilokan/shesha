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


def data_calculation(recs):
    discount_amount = discounted_amount = tax_amount = untaxed_amount = taxed_amount \
        = cgst = sgst = igst = sub_total_amount = 0
    for rec in recs:
        discount_amount = discount_amount + rec.discount_amount
        discounted_amount = discounted_amount + rec.discounted_amount
        tax_amount = tax_amount + rec.tax_amount
        untaxed_amount = untaxed_amount + rec.untaxed_amount
        taxed_amount = taxed_amount + rec.taxed_amount
        cgst = cgst + rec.cgst
        sgst = sgst + rec.sgst
        igst = igst + rec.igst
        sub_total_amount = sub_total_amount + rec.total_amount

    total_amount = sub_total_amount + rec.total_amount
    grand_total_amount = round(total_amount + tax_amount)
    round_off_amount = round(total_amount + tax_amount) - (total_amount + tax_amount)

    return {"discount_amount": discount_amount,
            "discounted_amount": discounted_amount,
            "tax_amount": tax_amount,
            "untaxed_amount": untaxed_amount,
            "taxed_amount": taxed_amount,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_amount": total_amount,
            "grand_total_amount": grand_total_amount,
            "round_off_amount": round_off_amount}


def dictionary_reset(recs, array):
    new_dict = {}

    for key, value in recs.iteritems():
        if key in array:
            new_dict[key] = value

    return new_dict
