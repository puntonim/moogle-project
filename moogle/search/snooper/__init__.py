from tokens.models import Provider, BearerToken
from utils.solr import Solr, CORE_NAMES


class Snooper:
    def __new__(cls, provider_name, user, *args, **kwargs):
        providers_snoopers_cls = {
            #Provider.NAME_GMAIL: GmailSnooper,
            #Provider.NAME_DRIVE: DriveSnooper,
            Provider.NAME_FACEBOOK: FacebookSnooper,
            Provider.NAME_DROPBOX: DropboxSnooper,
            Provider.NAME_TWITTER: TwitterSnooper,
        }
        snooper_cls = providers_snoopers_cls.get(provider_name, None)
        if snooper_cls:
            return snooper_cls(user)
        return cls

    @staticmethod
    def search(*args, **kwargs):
        return []


class BaseSolrSnooper:
    def search(self, q):
        bearertoken = BearerToken.objects.only(
            'id').get(user=self.user, provider__name=self.provider_name)
        fq = 'bearertoken_id:{}'.format(bearertoken.id)

        solr = Solr(CORE_NAMES[self.provider_name])
        r = solr.search(q=q, fq=fq, fl='id')
        return r.documents  # A list of dicts.


class GmailSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_GMAIL


class DriveSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_DRIVE


class FacebookSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_FACEBOOK


class DropboxSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_DROPBOX


class TwitterSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_TWITTER


