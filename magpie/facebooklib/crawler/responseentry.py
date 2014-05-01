

class FacebookResponseEntry:

    def __init__(self, entry_dict):
        """

        Parameters:
        entry_dict -- a Python dictionary like:
        {
            "updated_time": "2014-01-19T16:29:00+0000",
            "message": "Grazie\nThanks :)",
            "id": "10203300267177108"
        }
        """
        self.entry_dict = entry_dict

    @property
    def id(self):
        return self.entry_dict['id']

    @property
    def updated_time(self):
        return self.entry_dict['updated_time']

    @property
    def message(self):
        return self.entry_dict['message']