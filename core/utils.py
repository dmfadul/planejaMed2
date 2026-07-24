import unicodedata


def normalize_name_for_search(value: str) -> str:
    """
    Normalize a name for case-insensitive and accent-insensitive searching.

    Examples:
        "João da Silva"   -> "JOAO DA SILVA"
        "JOÃO  DA SILVA"  -> "JOAO DA SILVA"
        "  José Luís  "   -> "JOSE LUIS"
    """
    value = unicodedata.normalize("NFKD", value or "")

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )

    return " ".join(value.casefold().upper().split())