import requests
import json
from os.path import join, normpath
import logging

from utils.exceptions import SolrResponseError
from utils.dates import dropbox_date_to_solr_date
from magpie.settings import settings
from models import Provider


log = logging.getLogger('dropbox')


class DropboxSolrUpdater:
    CORE_NAME = settings.CORE_NAMES[Provider.NAME_DROPBOX]

    def __init__(self, bearertoken_id):
        self.bearertoken_id = bearertoken_id
        self.url = '{}/{}/update'.format(settings.SOLR_URL, self.CORE_NAME)

    def add(self, redis_entry, commit=False):
        local_file_path = normpath(join(settings.DROPBOX_TEMP_STORAGE_PATH,
                                        str(self.bearertoken_id),
                                        redis_entry.local_name))

        # Build Solr doc.
        doc = self._convert_redis_entry_to_solr_doc(redis_entry, local_file_path)
        r = self._post_file(doc, local_file_path)
        self._sanity_check(r, True)

        if commit:
            self.commit()

    def _convert_redis_entry_to_solr_doc(self, redis_entry, local_file_path):
        # Build the metadata-file path.
        metadata_file_path = '{}.metadata'.format(local_file_path)
        # Read the content of the metadata-file.
        with open(metadata_file_path) as fin:
            data = fin.read()
        # Load the content (json) of the metadata-file in a Python dictionary.
        metadata = json.loads(data)

        doc = dict()
        doc['literal.bearertoken_id'] = self.bearertoken_id
        doc['literal.id'] = redis_entry.id
        doc['literal.remote_path'] = metadata['path']
        doc['literal.modified_at'] = dropbox_date_to_solr_date(metadata['modified'])
        doc['literal.mime_type'] = metadata['mime_type']
        doc['literal.bytes'] = metadata['bytes']

        return doc

    def delete(self, redis_entry):
        """
        Delete `redis_entry`.
        """
        pass

    def reset(self, commit=False):
        """
        Delete all docs for `bearertoken_id`.
        """
        q = 'bearertoken_id:{}'.format(self.bearertoken_id)
        xml_data = '<delete><query>{}</query></delete>'.format(q)
        r = self._post_xml(xml_data)
        self._sanity_check(r)

        if commit:
            self.commit()

        return r

    def commit(self):
        xml_data = '<commit waitSearcher="true" expungeDeletes="false"/>'
        r = self._post_xml(xml_data)
        self._sanity_check(r)
        return r

    @staticmethod
    def _sanity_check(r, is_check_solr_response=False):
        if r.status_code != 200:
            raise SolrResponseError('HTTP Status: {}\n{}'.format(
                r.status_code, json.dumps(json.loads(r.text), indent=4))
            )

        if not is_check_solr_response:
            return

        solr_status = json.loads(r.text)['responseHeader']['status']
        if solr_status != 0:
            raise SolrResponseError('Solr Status: {}\n{}'.format(
                solr_status, json.dumps(json.loads(r.text), indent=4))
            )

    def _post_file(self, doc, local_file_path):
        """
        Post a file to add to Solr server.

        Parameters:
        doc -- doc to be added.
        local_file_path -- local path of the file to add.
        """
        # Build url params.
        params = doc
        params['wt'] = 'json'
        files = {'file': open(local_file_path, 'rb')}
        log.debug('Posting file to Solr: {}\nParams: {}'.format(self.url, params))
        # Send request.
        r = requests.post('{}/extract'.format(self.url), params=params, files=files)
        return r

    def _post_xml(self, xml):
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
        r = requests.post(self.url, data=xml_data, headers=headers)
        return r