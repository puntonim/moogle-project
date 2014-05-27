"""
Note: we can NOT assume that a Gmail account and a Drive account for a user share the same Google
profile, because a person can connect his personal Gmail account and his company's Drive.
"""
from requests_oauthlib import OAuth2Session

from tokens.models import BearerToken, Provider
from ..models import GmailProfile


class GmailProfiler:
    """
    Query Google on the behalf of a user to find profile details and store them in a GmailProfile.
    """
    def __init__(self, user, token_set=None):
        self.user = user
        self.provider = Provider.objects.get(name=Provider.NAME_GMAIL)
        if not token_set:
            bearertoken = BearerToken.objects.get(user=user, provider=self.provider)
            token_set = bearertoken.token_set
        self.token_set = token_set

    def fetch_profile_details(self):
        """
        Query the user profile and store it in Moogle.
        """
        data = self._query_profile_details()
        self._store_profile_details(data)

    def _query_profile_details(self):
        google = OAuth2Session(client_id=self.provider.client_id, token=self.token_set)
        resource_url = 'https://www.googleapis.com/userinfo/v2/me'
        r = google.get(resource_url)
        return r.json()  # Returns a dictionary.

    def _store_profile_details(self, data):
        """
        Store profile details into `GmailProfile`.

        Parameters:
        data -- a dictionary like:
        {
            "locale": "en",
            "family_name": "Doe",
            "email": "johndoe@gmail.com",
            "link": "https://profiles.google.com/353452857839983457489",
            "verified_email": true,
            "id": "353452857839983457489",
            "gender": "male",
            "given_name": "John",
            "name": "John Doe"
        }
        """
        profile, __ = GmailProfile.objects.get_or_create(user=self.user)
        profile.family_name = data.get('family_name', '')
        profile.given_name = data.get('given_name', '')
        profile.name = data.get('name', '')
        profile.gender = data.get('gender', '')
        profile.email = data.get('email', '')
        profile.verified_email = data.get('verified_email', None)
        profile.locale = data.get('locale', '')
        profile.google_id = data.get('id', '')
        profile.link = data.get('link', '')
        profile.save()