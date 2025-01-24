from typing import Any

def _clean_imported_excel_values(x: Any) -> Any | None:
    """
    Clean a value from Excel import.
    This is necessary as Excel allows for heterogenous column and row values.
    Ex: 'No VAT' can be found in a column with numeric values.
    """
    if isinstance(x, str):
        # Check if its a double-dot (e.g. a functional None value)
        if x == "..":
            return None

        # Check if there are any non-numeric characters in the string.
        x = x.strip()
        for char in x:
            if char.isalpha() and char not in ['.', ',', '-']:
                return None

        # Fix broken floats.
        if "." in x:
            if x.startswith('.'):
                x = '0' + x
                return float(x)

        # Try to coerce to an integer, then a float.
        try:
            return int(x)
        except (ValueError, TypeError):
            try:
                return float(x)
            except (ValueError, TypeError):
                return x
    else:
        return x