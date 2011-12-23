from hopper.files import BaseFile, JSONFile

class User(JSONFile):
    """Represents a user."""

    def __init__(self, container, id=None):
        self.fields = {
            'name': None,
            'email': None,
            'password': None,
            'avatar': None
            }

        if id is not None:
            self.id = self._resolve_id(id)
            self.from_file()
        super(BaseFile, self).__init__()
