
def run(phone: str) -> str:
    import re
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return digits.zfill(10)[:10]  # Возвращаем первые 10 циф