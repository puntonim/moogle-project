from os.path import splitext, basename
from mysolr import Solr as MySolr
from mysolr.response import SolrResponse
import requests

from magpie.settings import settings
from .exceptions import SolrResponseError
from models import Provider


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
    It adds features missing in `mysolr`, like delete by query or add file.
    """
    def __init__(self, core_name):
        self.url = '{}/{}'.format(settings.SOLR_URL, core_name)

    @property
    def _mysolr(self):
        # TODO: This thing of caching mysolr will be useless with mysolr 0.9, because it has the
        # TODO: ability to re-use the same requests.session, like:
        # TODO: session = requests.Session()
        # TODO: solr = Solr('http://localhost:8983/solr/collection1', make_request=session)
        # TODO: see http://mysolr.redtuna.org/en/latest/user/userguide.html
        try:
            return self._mysolr_cache
        except AttributeError:
            self._mysolr_cache = MySolr(self.url, version=4)
            return self._mysolr_cache

    def update(self, *args, **kwargs):
        """
        Add/update a doc in Solr.
        It uses mysolr library.
        """
        r = self._mysolr.update(*args, **kwargs)
        self._sanity_check(r, True)

    def search(self, *args, **kwargs):
        """
        Search in Solr.
        It uses mysolr library.
        """
        r = self._mysolr.search(*args, **kwargs)
        self._sanity_check(r, True)
        return r

    def add_file(self, doc, local_file_path):
        """
        Post a file to add to Solr server.
        It uses requests library because mysolr library has no such a functionality.

        Parameters:
        doc -- doc to be added.
        local_file_path -- local path of the file to add.
        """
        # Build url params.
        params = doc
        params['wt'] = 'json'
        # Normally we would use the following dictionary to attach a file to a `requests.post`:
        #files = {'file': open(local_file_path, 'rb')}
        # But this would fail silently when the file name contains special chars (like
        # Chinese chars). The failure is subtle because the `requests.post` does not raise
        # any exception, it just posts no file at all.
        # To solve this we need to assign a fake name to the file.
        ext = splitext(basename(local_file_path))[1]  # Get the extension of the original file.
        # This way the posted file will be named: doc`.ext`.
        files = {'doc': ('doc' + ext, open(local_file_path, 'rb'))}

        # Send request.
        r = requests.post('{}/update/extract'.format(self.url), params=params, files=files)
        self._sanity_check(SolrResponse(r), True)

    def delete_by_query(self, query):
        """
        Delete docs from Solr according to a query.
        It uses requests library because mysolr library has no such a functionality.

        Parameters:
        query -- query to identify the elements to delete.
        """
        xml_data = '<delete><query>{}</query></delete>'.format(query)
        r = self._post_xml(xml_data)
        self._sanity_check(SolrResponse(r), True)

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

    def _post_xml(self, xml):
        """
        Send the xml to Solr server.
        It uses requests library because mysolr library has no such a functionality.

        Parameters:
        xml -- XML document to be posted.
        """
        xml_data = xml.encode('utf-8')
        headers = {
            'Content-type': 'text/xml; charset=utf-8',
            'Content-Length': "%s" % len(xml_data)
        }
        params = dict()
        params['wt'] = 'json'
        r = requests.post('{}/update'.format(self.url), params=params, data=xml_data,
                          headers=headers)
        return r