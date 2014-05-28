import urllib
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from ..snooper import BaseSolrSnooper
from tokens.models import Provider, BearerToken


class DriveSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        #self.provider_name = Provider.NAME_DRIVE
        self.provider = Provider.objects.get(name=Provider.NAME_DRIVE)
        self.bearertoken = BearerToken.objects.get(user=user,
                                                   provider=self.provider)

    def search(self, q):
        google = OAuth2Session(self.provider.client_id, token=self.bearertoken.token_set)

        # Get search criteria entered by the user
        ##owner = request.POST.get('owner', True)
        ##trash = request.POST.get('trash', None)

        # Get the next page url
        ##next_page = request.GET.get('next', None)

        ##if next_page:
        ##    resource_url = urllib.parse.unquote(next_page)

        # Build the URL of the protected resource
        # Compose the full query parameters
        q_val = "fullText contains '{}' and trashed = false".format(q)
        ##if owner:
        ##    q_val += " and 'puntonim@gmail.com' in owners"
        ##if trash:
        ##    q_val = q_val.replace(' and trashed = false', '')

        # Build args for the query
        args = {
            'q': q_val,
            'maxResults': 10, ##results_per_page,
            'fields': 'nextLink,items(title,originalFilename,fileExtension,mimeType,kind,fileSize,modifiedDate,'
                      'createdDate,ownerNames,owners,thumbnailLink,webContentLink,alternateLink,iconLink,exportLinks,'
                      'embedLink)',
        }
        resource_url = 'https://www.googleapis.com/drive/v2/files?{}'.format(urllib.parse.urlencode(args))


        # Fetch teh protected resource
        try:
            r = google.get(resource_url)
        except TokenExpiredError:
            refresh_extra_args = {'client_id': self.provider.client_id,
                                  'client_secret': self.provider.client_secret}
            token = google.refresh_token(self.provider.token_url,
                                         refresh_token=self.bearertoken.refresh_token,
                                         **refresh_extra_args)
            ##save_token(token, request.user)
            google = OAuth2Session(self.provider.client_id, token=token)
            r = google.get(resource_url)

        # There are 2 ways to check if the current token has expired:
        # 1) Automatic refresh. The token comes with a "expires_in": 3600 field. So we can keep track of the time the token
        #    has been generated, then update this value the moment we use the token. If the value is 0 or a negative number
        #    then the automatic refresh will take care of it
        # 2) Run a query and if we get the status_code 401 means that the token has expired. So we ask for a refresh.
        #
        # 1st SOLUTION: Create a new session with automatic refresh
        # The refresh is triggered by the attribute expires_in of the token and it is up to me to keep its value updated
        # Then it's just to complicated and the solution 2 is better
        # http://requests-oauthlib.readthedocs.org/en/latest/oauth2_workflow.html
        # Set the extra params Google wants in case of refresh
        #auto_refresh_extra_args = {'client_id': client_id, 'client_secret': client_secret}
        #google = OAuth2Session(client_id, token=access_token, auto_refresh_url=token_url, token_updater=save_token, auto_refresh_kwargs=auto_refresh_extra_args)
        #
        # 2nd SOLUTION: Check the status code
        # 2.1. Monkey patch the get method of OAuth2Session in order to raise a TokenExpiredError
        # It's cool but looks like too complicated
        #from oauthlib.oauth2 import TokenExpiredError
        #def patched_get(self, *args, **kwargs):
        #    r = self.original_get(*args, **kwargs)
        #    if r.status_code == 401:
        #        print("err")
        #        raise TokenExpiredError
        #    return r
        #OAuth2Session.original_get = OAuth2Session.get
        #OAuth2Session.get = patched_get
        #
        # 2.2. Check the status code and in case run the refresh and repeat the query
        ##if r.status_code == 401:
        ##    refresh_extra_args = {'client_id': self.provider.client_id,
        ##                          'client_secret': self.provider.client_secret}
        ##    token = google.refresh_token(self.provider.token_url,
        ##                                 refresh_token=self.bearertoken.refresh_token,
        ##                                 **refresh_extra_args)
        ##    ##save_token(token, request.user)
        ##    google = OAuth2Session(self.provider.client_id, token=token)
        ##    r = google.get(resource_url)

        results = r.json()  # returns a dictionary

        # Prepare next page link
        ##next_page = results.get('nextLink', None)
        ##if next_page:
        ##    args = {'next': next_page}
        ##    next_page = "{}?{}".format(reverse('drive_query'), urllib.parse.urlencode(args))

        import json
        print(json.dumps(results.get('items'), indent=4))
        #print(results.get('items', None))
        return results.get('items', list())