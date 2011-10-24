class BadReference(Exception):
    """No object matches the identifier."""
    pass

class AmbiguousReference(Exception):
    """Multiple objects match the identifier."""
    pass
