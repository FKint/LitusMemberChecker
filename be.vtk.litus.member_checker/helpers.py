import re


def is_valid_barcode(entry):
    return re.match('[0-9]{1,12}$', entry) is not None


def is_valid_identification(entry):
    return re.match('[rsu][0-9]{7}$', entry) is not None


assert is_valid_identification('r0123456') == True
assert is_valid_identification('r234') == False

assert is_valid_barcode('978131403635') == True
assert is_valid_identification('r234') == False
