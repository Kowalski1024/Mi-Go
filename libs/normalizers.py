import re
import unicodedata


def title_normalizer(string, allow_unicode=False) -> str:
    """
    Normalizes a string to be used as a title

    Args:
        string: string to normalize
        allow_unicode: whether to allow unicode characters

    Returns:
        normalized string
    """

    string = str(string)
    # remove all non-ascii characters
    if allow_unicode:
        string = unicodedata.normalize("NFKC", string)
    else:
        string = (
            unicodedata.normalize("NFKD", string)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    string = re.sub(r"[^\w\s-]", "", string.lower())

    return re.sub(r"[-\s]+", "-", string).strip("-_")
