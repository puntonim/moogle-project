

class TwitterResponseEntry:

    def __init__(self, entry_dict):
        """

        Parameters:
        entry_dict -- a Python dictionary like:
        {
            "in_reply_to_status_id": null,
            "in_reply_to_screen_name": null,
            "id_str": "453848727191830528",
            "text": "#Brunetta \"non sei degno di essere nano\"",
            "in_reply_to_user_id": null,
            "coordinates": null,
            "geo": null,
            "source": "web",
            "retweeted": false,
            "id": 453848727191830528,
            "user": {
                "id_str": "135348442",
                "id": 135348442
            },
            "in_reply_to_status_id_str": null,
            "entities": {
                "urls": [],
                "hashtags": [
                    {
                        "indices": [
                            0,
                            9
                        ],
                        "text": "Brunetta"
                    }
                ],
                "symbols": [],
                "user_mentions": []
            },
            "contributors": null,
            "truncated": false,
            "created_at": "Wed Apr 09 10:55:43 +0000 2014",
            "favorited": false,
            "favorite_count": 0,
            "place": null,
            "in_reply_to_user_id_str": null,
            "retweet_count": 0,
            "lang": "it"
        }
        """
        self.entry_dict = entry_dict

    @property
    def id_str(self):
        return self.entry_dict['id_str']