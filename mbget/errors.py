class Error(Exception):
    """
    Base Class for exceptions in the module
    """

    def __init__(self, message: str):
        self.message = message


class ManifestError(Error):
    def __init__(self, message):
        Error.__init__(self, message)


class UpdateError(Error):
    """An Update specific error"""

    def __init__(self, message):
        Error.__init__(self, message)
