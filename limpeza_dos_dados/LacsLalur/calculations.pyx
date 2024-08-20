# cython: language_level=3

import pandas as pd

def lucroAntesCSLL(lacsFiltrado, data):
    lacs = lacsFiltrado
    lacs = lacs[(lacs['Código Lançamento e-Lacs'] == 2) & (lacs['Data Inicial'].str.contains(data))]
    lucroAntCSLL = lacs['Vlr Lançamento e-Lacs'].sum()
    return lucroAntCSLL