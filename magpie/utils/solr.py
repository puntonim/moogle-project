from os.path import splitext, basename
from mysolr import Solr
import requests
import json

from magpie.settings import settings
from utils.exceptions import SolrResponseError


class Solr:
    """
    A wrapper around `mysolr` library.
    It adds
    """
    def __init__(self, core_name):
        self.url = '{}/{}'.format(settings.SOLR_URL, core_name)

    @property
    def _mysolr(self):
        try:
            return self._mysolr_cache
        except AttributeError:
            self._mysolr_cache = Solr(self.url)
            return self._mysolr_cache

    def update(self, *args, **kwargs):
        r = self._mysolr.update(*args, **kwargs)
        self._sanity_check(r, True)

    @staticmethod
    def _sanity_check(r, is_check_solr_response=False):
        if r.status != 200:
            raise SolrResponseError('HTTP Status: {}\n{}'.format(
                r.status, r.raw_content)
            )

        if is_check_solr_response:
            if r.solr_status != 0:
                raise SolrResponseError('Solr Status: {}\n{}'.format(
                    r.solr_status, r.raw_content)
                )

    def commit(self):
        r = self.solr.commit()
        self._sanity_check(r)























def escape_solr_query(query):
    """
    Escape special chars for Solr queries.
    """
    chars = ['+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?',
             ':', '/', ' ']
    for char in chars:
        query = query.replace(char, '\{}'.format(char))

    return query


def add_file(url, doc, local_file_path):
    """
    Post a file to add to Solr server.

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
    r = requests.post('{}/extract'.format(url), params=params, files=files)
    _sanity_check(r)


def delete_by_query(url, query):
    """
    Delete docs from Solr according to a query.

    Parameters:
    query -- query to identify the elements to delete.
    """
    xml_data = '<delete><query>{}</query></delete>'.format(query)
    r = _post_xml(url, xml_data)
    _sanity_check(r)


def commit(url):
    xml_data = '<commit waitSearcher="true" expungeDeletes="false"/>'
    r = _post_xml(url, xml_data)
    _sanity_check(r, False)


def _post_xml(url, xml):
    """
    Send the xml to Solr server.

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
    r = requests.post(url, params=params, data=xml_data, headers=headers)
    return r


def _sanity_check(r, is_check_solr_response=True):
    if r.status_code != 200:
        raise SolrResponseError('HTTP Status: {}\n{}'.format(
            r.status_code, json.dumps(json.loads(r.text), indent=4))
        )

    if not is_check_solr_response:
        return

    solr_status = json.loads(r.text)['responseHeader']['status']
    if solr_status != 0:
        raise SolrResponseError('Solr Status: {}\n{}'.format(
            solr_status, json.dumps(json.loads(r.text), indent=4)))