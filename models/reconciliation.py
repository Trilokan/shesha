
# Date: October 9, 2018
# Algorithm: Reconciliation Algorithm
# Input two records reconcile each other
# Input {'id': 0, 'ref': 'xxx', 'amount': 000}
# Output {'id': 0, 'ref': 'xxx', 'amount': 000, 'result' : {'amount': 000,
#                                               'reconcile': 000,
#                                               'balance': 000}}


def create_obj_result(obj):
    obj["result"] = {"amount": obj["amount"],
                     "reconcile": 0,
                     "balance": 0}
    return obj


def reconciliation(cr_obj, dr_obj):
    for cr in cr_obj:
        cr = create_obj_result(cr)

        value = (cr["result"]["amount"] - cr["result"]["reconcile"])

        for dr in dr_obj:
            dr = create_obj_result(dr)

            diff = dr["result"]["amount"] - dr["result"]["reconcile"]

            if (diff > 0) and (value > 0):
                cr["reconcile"] = dr["reconcile"] = True

                if diff >= value:
                    dr["result"]["reconcile"] = dr["result"]["reconcile"] + value
                    cr["result"]["reconcile"] = cr["result"]["reconcile"] + value
                else:
                    dr["result"]["reconcile"] = dr["result"]["reconcile"] + diff
                    cr["result"]["reconcile"] = cr["result"]["reconcile"] - diff

                cr["result"]["balance"] = cr["result"]["amount"] - cr["result"]["reconcile"]
                dr["result"]["balance"] = dr["result"]["amount"] - dr["result"]["reconcile"]

    return cr_obj, dr_obj
