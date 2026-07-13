from decimal import Decimal, InvalidOperation


def parse_brl(value: str | int | float | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    if isinstance(value, int | float):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    clean = (
        value.replace("R$", "")
        .replace("\xa0", " ")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )
    if not clean:
        return None
    try:
        return Decimal(clean).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def format_brl(value: Decimal | None) -> str:
    if value is None:
        return "R$ --"
    number = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {number}"

