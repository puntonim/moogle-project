from tokens.models import Provider, BearerToken
from utils.solr import Solr, CORE_NAMES


class Snooper:
    def __new__(cls, provider_name, user, *args, **kwargs):
        # Imports from here to avoid circular import problems w/ those modules.
        from .facebook import FacebookSnooper
        from .dropbox import DropboxSnooper
        from .twitter import TwitterSnooper
        from .gmail import GmailSnooper
        from .drive import DriveSnooper

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
        """
        Default search which returns no results.
        """
        return []


class BaseSolrSnooper:
    extra_query_args = dict()

    def search(self, q):
        bearertoken = BearerToken.objects.only(
            'id').get(user=self.user, provider__name=self.provider_name)
        fq = 'bearertoken_id:{}'.format(bearertoken.id)

        solr = Solr(CORE_NAMES[self.provider_name])
        r = solr.search(q=q, fq=fq, **self.extra_query_args)
        return r.documents  # A list of dicts.