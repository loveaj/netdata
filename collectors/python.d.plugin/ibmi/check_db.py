#! /usr/bin/python3

try:
    import ibm_db_dbi
    HAS_IBMI = True
except ImportError:
    HAS_IBMI = False

print(ibm_db_dbi.apilevel)      # expectiong "2.0"
