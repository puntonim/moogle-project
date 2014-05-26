# Stdlib imports
from abc import ABCMeta, abstractmethod

# Core Django imports

# Third-party app imports
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from requests_oauthlib import OAuth2Session, OAuth1Session

# Imports from local apps
from .models import Provider, BearerToken
from profiles.profiler.gmail import GmailProfiler


class AbstractOauthFlowManager(metaclass=ABCMeta):
    # Terminology:
    # http://tools.ietf.org/html/rfc6750
    # http://hueniverse.com/oauth/
    # http://oauth.net/
    # https://en.wikipedia.org/wiki/OAuth

    def __init__(self):
        # Set the provider based on the `PROVIDER_NAME` class attribute
        self.provider = Provider.objects.get(name=self.__class__.PROVIDER_NAME)

    def step1(self, request):
        oauth_sex = self._create_oauth_sex()
        authorization_url, csrf_code = self._get_authorization_url(oauth_sex)

        # Store csrf_code to prevent CSRF (OAuth1 has no such code)
        if csrf_code:
            request.session['csrf_code'] = csrf_code

        return authorization_url

    def step2(self, request):
        self._prevent_csrf(request)

        auth_code = request.GET.get('code', None)
        sex = self._create_oauth_sex()
        token_set = self._fetch_token(sex, auth_code, request)

        # Save the new token
        self._save_token(token_set, request.user)

        # TODO: Query and save profile info.
        # TODO: This should be a task run asynchronously.
        self.fetch_profile_details(request.user, token_set)

    def _create_oauth_sex(self):
        sex = OAuth2Session(
            self.provider.client_id,
            scope=self.provider.scope,
            # TODO: fix this to a proper url
            redirect_uri='http://127.0.0.1:8000' + self.provider.redirect_url
        )
        return self._compliance_fix(sex)

    def _compliance_fix(self, oauth_sex):
        """
        Add a compliance fix to the `OAuth2Session` in order to make it work with a specific
        provider. Facebook needs it for instance.
        The default behavior implemented in the superclass does nothing but returning the session.
        This method is meant to be overwritten by subclasses that need it (like Facebook).
        """
        return oauth_sex

    def _save_token(self, token_set, user):
        tk, _ = BearerToken.objects.get_or_create(user=user, provider=self.provider)
        tk.token_set = token_set
        tk.save()
        return tk

    def _prevent_csrf(self, request):
        """Check csrf_code to prevent CSRF"""

        # The `state` GET argument received from the provider in step2 must match the `csrf_code`
        # stored in the user session during step1

        csrf_code = request.GET.get('state', 'default')

        if csrf_code != request.session.pop('csrf_code', None):
            # Raise an exception
            # This will generate a HTTP 500 Server error page
            msg = ("{}: the state parameter received in step2 doesn't match the one in step1. "
                   "This can be a security issue.".format(self.__class__.__name__))
            raise Exception(msg)

    def _fetch_token(self, oauth_sex, auth_code, *args):
        return oauth_sex.fetch_token(
            self.provider.token_url,
            client_secret=self.provider.client_secret,
            code=auth_code
        )

    @abstractmethod
    def _get_authorization_url(self, oauth_sex):
        pass

    @abstractmethod
    def fetch_profile_details(self, user, token_set):
        pass


class DriveOauthFlowManager(AbstractOauthFlowManager):
    PROVIDER_NAME = Provider.NAME_DRIVE

    def _get_authorization_url(self, oauth_sex):
        # `authorization_url` parameters:
        # access_type:
        #     Indicates whether your application needs to access a Google API when the user is not
        #     present at the browser. This parameter defaults to online. If your application needs
        #     to refresh access tokens when the user is not present at the browser, then use
        #     offline. This will result in your application obtaining a refresh token the first
        #     time your application exchanges an authorization code for a user.
        # approval_prompt:
        #     Indicates whether the user should be re-prompted for consent. The default is auto,
        #     so a given user should only see the consent page for a given set of scopes the first
        #     time through the sequence. If the value is force, then the user sees a consent page
        #     even if they previously gave consent to your application for a given set of scopes.
        authorization_url, csrf_code = oauth_sex.authorization_url(
            self.provider.authorization_base_url,
            access_type="offline"
        )
        return authorization_url, csrf_code

    def fetch_profile_details(self, user, token_set):
        pass


class GmailOauthFlowManager(AbstractOauthFlowManager):
    PROVIDER_NAME = Provider.NAME_GMAIL

    def _get_authorization_url(self, oauth_sex):
        # `authorization_url` parameters:
        # access_type:
        #     Indicates whether your application needs to access a Google API when the user is not
        #     present at the browser. This parameter defaults to online. If your application needs
        #     to refresh access tokens when the user is not present at the browser, then use
        #     offline. This will result in your application obtaining a refresh token the first
        #     time your application exchanges an authorization code for a user.
        # approval_prompt:
        #     Indicates whether the user should be re-prompted for consent. The default is auto,
        #     so a given user should only see the consent page for a given set of scopes the first
        #     time through the sequence. If the value is force, then the user sees a consent page
        #     even if they previously gave consent to your application for a given set of scopes.
        authorization_url, csrf_code = oauth_sex.authorization_url(
            self.provider.authorization_base_url,
            access_type="offline"
        )
        return authorization_url, csrf_code

    def fetch_profile_details(self, user, token_set):
        profiler = GmailProfiler(user, token_set)
        profiler.fetch_profile_details()


class FacebookOauthFlowManager(AbstractOauthFlowManager):
    PROVIDER_NAME = Provider.NAME_FACEBOOK

    def _get_authorization_url(self, oauth_sex):
        authorization_url, csrf_code = oauth_sex.authorization_url(
            self.provider.authorization_base_url,
            display='page'
        )
        return authorization_url, csrf_code

    def _compliance_fix(self, oauth_sex):
        """
        Add a compliance fix to the `OAuth2Session` in order to make it work with Facebook.
        """
        return facebook_compliance_fix(oauth_sex)

    def fetch_profile_details(self, user, token_set):
        pass


class TwitterOauthFlowManager(AbstractOauthFlowManager):
    PROVIDER_NAME = Provider.NAME_TWITTER

    def _create_oauth_sex(self):
        return OAuth1Session(
            self.provider.client_id,
            client_secret=self.provider.client_secret,
            # TODO: fix this to a proper url
            callback_uri='http://127.0.0.1:8000' + self.provider.redirect_url)

    def _get_authorization_url(self, oauth_sex):
        # Twitter uses OAuth1.0a which requires a step before getting the authorization_url
        oauth_sex.fetch_request_token(self.provider.request_token_url)

        authorization_url = oauth_sex.authorization_url(
            self.provider.authorization_base_url,)
        return authorization_url, None

    def _prevent_csrf(self, request):
        # There is no CSRF protection in OAuth1
        pass

    def _fetch_token(self, oauth_sex, _, request):
        oauth_sex.parse_authorization_response(request.build_absolute_uri())
        return oauth_sex.fetch_access_token(
            self.provider.token_url,)

    def fetch_profile_details(self, user, token_set):
        pass


class DropboxOauthFlowManager(AbstractOauthFlowManager):
    PROVIDER_NAME = Provider.NAME_DROPBOX

    def _get_authorization_url(self, oauth_sex):
        authorization_url, csrf_code = oauth_sex.authorization_url(
            self.provider.authorization_base_url
        )
        return authorization_url, csrf_code

    def fetch_profile_details(self, user, token_set):
        pass


class OAuthFlowMangerFactory:
    """
    Abstract Factory o Abstract Method ???? pattern
    """
    _factory_map = {
        Provider.NAME_DRIVE: DriveOauthFlowManager,
        Provider.NAME_GMAIL: GmailOauthFlowManager,
        Provider.NAME_FACEBOOK: FacebookOauthFlowManager,
        Provider.NAME_TWITTER: TwitterOauthFlowManager,
        Provider.NAME_DROPBOX: DropboxOauthFlowManager,
    }

    @staticmethod
    def create_oauth_flow_manger(provider):
        """
        Factory method to create the right subclass of AbstractOauthFlowManager based
        on `provider`.

        Parameters:
        provider -- a `Provider`.

        Return:
        a subclass of AbstractOauthFlowManager.
        """

        # This factory method could be a simple module-level function, but I prefer to put
        # this code into this class as a static method

        try:
            return OAuthFlowMangerFactory._factory_map[provider.name]()
        except KeyError as ex:
            msg = "There is no OauthFlowManager class for {}".format(provider.name)
            raise NotImplementedError(msg) from ex
