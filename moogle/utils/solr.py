from mysolr import Solr as MySolr

from django.conf import settings

from .exceptions import SolrResponseError
from tokens.models import Provider


CORE_NAMES = {
    Provider.NAME_TWITTER: 'twitter',
    Provider.NAME_FACEBOOK: 'facebook',
    Provider.NAME_DROPBOX: 'dropbox'
}


def escape_solr_query(query):
    """
    Escape special chars for Solr queries.
    """
    chars = ['+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?',
             ':', '/', ' ']
    for char in chars:
        query = query.replace(char, '\{}'.format(char))

    return query


class Solr:
    """
    A wrapper around `mysolr` library.
    """
    def __init__(self, core_name):
        self.url = '{}/{}'.format(settings.SOLR_URL, core_name)

    @property
    def _mysolr(self):
        # TODO: This thing of caching mysolr will be useless with mysolr 0.9, because it has the
        # TODO: ability to resuse the same requests.session, like:
        # TODO: session = requests.Session()
        # TODO: solr = Solr('http://localhost:8983/solr/collection1', make_request=session)
        # TODO: see http://mysolr.redtuna.org/en/latest/user/userguide.html
        try:
            return self._mysolr_cache
        except AttributeError:
            self._mysolr_cache = MySolr(self.url)
            return self._mysolr_cache

    def search(self, *args, **kwargs):
        """
        Search in Solr.
        It uses mysolr library.
        """
        r = self._mysolr.search(*args, **kwargs)
        self._sanity_check(r, True)
        return r

    def search_cursor(self, *args, **kwargs):
        """
        Search in Solr using a cursor to navigate next results.
        It uses mysolr library.
        """
        # TODO: change this such as there is an automatic sanity_check
        # TODO: then update also change_bearertoken_by_query() in solr_extra.py
        cur = self._mysolr.search_cursor(*args, **kwargs)
        ####self._sanity_check(r, True)
        return cur

    def commit(self):
        """
        Send a commit to Solr.
        It uses mysolr library.
        """
        r = self._mysolr.commit()
        self._sanity_check(r)

    @staticmethod
    def _sanity_check(r, is_check_solr_response=False):
        """
        Check whether a `mysolr.SolrResponse` is ok.
        Tip: you can easily convert a `requests.models.Response` to `mysolr.SolrResponse` like:
        mysolr.SolrResponse(requests.models.Response).
        """
        if r.status != 200:
            raise SolrResponseError('HTTP Status: {}\n{}'.format(
                r.status, r.raw_content)
            )

        if is_check_solr_response:
            if r.solr_status != 0:
                raise SolrResponseError('Solr Status: {}\n{}'.format(
                    r.solr_status, r.raw_content))