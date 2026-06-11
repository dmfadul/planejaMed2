import unicodedata


COLLATION_NAME = "PORTUGUESE_NOCASE"


def normalize_for_sort(value):
    if value is None:
        return ""

    value = str(value).casefold()

    # João -> João, then remove the accent mark
    value = unicodedata.normalize("NFD", value)
    value = "".join(
        char for char in value
        if unicodedata.category(char) != "Mn"
    )

    return value


def portuguese_nocase_collation(a, b):
    a_norm = normalize_for_sort(a)
    b_norm = normalize_for_sort(b)

    if a_norm < b_norm:
        return -1
    if a_norm > b_norm:
        return 1

    return 0


def register_sqlite_collations(connection):
    connection.create_collation(
        COLLATION_NAME,
        portuguese_nocase_collation,
    )