def resolve_page(page: str | int, total: int, page_size: int) -> int:
    try:
        page_str = str(page).strip().lower() if page is not None else "1"
    except Exception:
        page_str = "1"
    if page_str in ("primeira", "first"):
        num = 1
    elif page_str in ("última", "ultima", "last"):
        num = max((total + page_size - 1) // page_size, 1)
    else:
        try:
            num = max(int(page_str), 1)
        except ValueError:
            num = 1
    # clamp
    last_page = max((total + page_size - 1) // page_size, 1)
    if num > last_page:
        num = last_page
    return num


def resolve_order(order: str | None) -> str:
    o = (order or "asc").strip().lower()
    if o in ("desc", "decrescente"):
        return "desc"
    # default asc, accepts "asc" and "crescente"
    return "asc"