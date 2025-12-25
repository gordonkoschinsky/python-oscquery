disallowed_path_chars = (
    " ",
    "#",
    "*",
    ",",
    "?",
    "[",
    "]",
    "{",
    "}",
)


def is_valid_path(path: str) -> bool:
    """Check if path contains characters that are not allowed by the OSC specification.
    Won't check for forward slash '/', since this will be used to split the path into containers and methods"""

    if any([x in path for x in disallowed_path_chars]):
        return False
    return True
