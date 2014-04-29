import re


class TwitterResponseEntry:

    def __init__(self, entry_dict):
        """

        Parameters:
        entry_dict -- a Python dictionary like:
        {
            "in_reply_to_status_id": null,
            "in_reply_to_screen_name": null,
            "id_str": "453848727191830528",
            "text": "#Superman said \"Hello world\"",
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
                        "text": "Superman"
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
        self.urls = list()
        self.media = list()

    @property
    def id_str(self):
        return self.entry_dict['id_str']

    @property
    def text(self):
        #return self.entry_dict['text'].encode('ascii', 'backslashreplace')
        return self.entry_dict['text']
    @property
    def lang(self):
        return self.entry_dict['lang']

    @property
    def created_at(self):
        return self.entry_dict['created_at']

    @property
    def retweeted(self):
        return self.entry_dict['retweeted']


    @property
    def text_clean(self):
        try:
            return self._text_clean
        except AttributeError:
            self._extract_urls_and_media()
            return self._text_clean

    def _extract_urls_and_media(self):
        indices = list()  # list of indices to remove
        self._text_clean = self.text
        entities = self.entry_dict.get('entities', {})

        # Get indices from urls
        urls = entities.get('urls', ())
        for url in urls:
            self.urls.append(url.get('expanded_url', ()))
            i = url.get('indices', ())
            indices.append((i[0], i[1]))

        # Get indices from media
        media = entities.get('media', ())
        for medium in media:
            self.media.append(medium.get('expanded_url', ()))
            i = medium.get('indices', ())
            indices.append((i[0], i[1]))

        # Now `indices` is a list of tuples, where each tuple is (x, y) where x and y are the
        # start and end of the url to remove from `self.text`.
        # We must order `indices` based on the starting indices, reverse.
        # Then we can remove the urls from `self.text`.
        indices = sorted(indices, key=lambda x: x[1], reverse=True)
        for ix in indices:
            #self._text_clean = self._text_clean.replace(self._text_clean[ix[0]:ix[1]], '')
            self._text_clean = self._text_clean[:ix[0]] + self._text_clean[ix[1]:]

        # Oldest tweets have no `urls` list in `entities` dictionary, they are just hard coded
        # in `self.text`. We must use a regex to remove them.
        # How do we know if this is an old tweet? We assume that any tweet with no `indices` is
        # an old-style tweet.
        # Also notice that if a tweet ends with the ellipsis character (u'\u2026'), or with
        # '...' for old-style tweets, this means that it is a retweet and it has been truncated.
        # If it is this case and if there a URL at the end of the status and this URL has
        # been truncated, then the `indices` contains only the info to cut out the ellipsis
        # character, like (139, 140), and not the url. So we need to process also this case.
        if not indices or self.text[-1:] == u'\u2026' or self.text[-3:] == '...':
            # Regex to identify URLs
            regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
                     '(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            urls = re.findall(regex, self._text_clean)
            for u in urls:
                self._text_clean = self._text_clean.replace(u, '')
            # Add the URLs found to `self.urls`
            self.urls.extend(urls)

            # Clean out any sort of 'http:/ ..' left at the end of the retweet like in:
            # "RT @googlemaps: Thx to the previewers who helped us build the #newGoogleMaps.
            # Beginning today it rolls out to users around the world http:/<ellipsis>"
            regex = u'\s*ht(t|tps?|tps?:|tps?:/|tps?://)?\s*(\.|\u2026)*$'
            self._text_clean = re.sub(regex, '', self._text_clean.strip()).strip()