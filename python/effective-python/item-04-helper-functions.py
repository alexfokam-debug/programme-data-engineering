"""
Effective Python - Item 04
Semaine S02

Objectif :
Comprendre quand extraire une expression complexe
dans une fonction auxiliaire.
"""


# ==========================================
# 01 - Données de départ
# ==========================================
row = {
    'user_id': 12345,
    'amount': '$1,234.56',
    'date': '2024-06-01',
    'discount': '10%'
}
# ==========================================
# 02 - Version initiale
# ==========================================

final_amount = float(row['amount'].replace('$','').replace(',','')) * (1 - float(row['discount'].replace('%',''))/100)


# ==========================================
# 03 - Version avec helper function
# ==========================================

def calculate_final_amount(amount_str, discount_str):

    if amount_str == "":
        return 0

    amount = float(
        amount_str.replace("$", "").replace(",", "")
    )

    if discount_str == "":
        discount = 0
    else:
        discount = float(
            discount_str.replace("%", "")
        ) / 100

    return amount * (1 - discount)


# ==========================================
# 04 - Vérification
# ==========================================

print(final_amount)  # Affiche le montant final calculé avec la version initiale
print(calculate_final_amount(row['amount'], row['discount']))  # Affiche le montant final calculé avec la fonction auxiliaire

print(calculate_final_amount("$100.00", "10%"))
print(calculate_final_amount("", "10%"))
print(calculate_final_amount("", ""))

