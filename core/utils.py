import unicodedata


def normalize_name_for_search(value: str) -> str:
    """
    Normalize text for case-insensitive and accent-insensitive searching.

    Examples:
        "João da Silva" -> "joao da silva"
        "JOÃO  DA SILVA" -> "joao da silva"
    """
    value = unicodedata.normalize("NFKD", value or "")

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )

    return " ".join(value.casefold().split())