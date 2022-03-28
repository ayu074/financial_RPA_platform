def format_number(num: str) -> str:
    result = ''
    try:
        num_type = float(num)
        result = '{:,.2f}'.format(num_type)
    except Exception:
        result = num
    finally:
        return result
