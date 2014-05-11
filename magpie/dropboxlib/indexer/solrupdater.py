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
        self.url = '{}/{}/update/extract'.format(settings.SOLR_URL, self.CORE_NAME)

    def add(self, redis_entry, commit=False):
        local_file_path = normpath(join(settings.DROPBOX_TEMP_STORAGE_PATH,
                                        str(self.bearertoken_id),
                                        redis_entry.local_name))

        # Build Solr doc.
        doc = self._convert_redis_entry_to_solr_doc(redis_entry, local_file_path)
        # Build url params.
        params = doc
        params['wt'] = 'json'
        files = {'file': open(local_file_path, 'rb')}
        # Send request.
        r = requests.post(self.url, params=params, files=files)
        self._sanity_check(r, True)
        log.debug('Request to Solr: {}\nParams: {}'.format(self.url, params))

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

    def reset(self):
        """
        Delete all docs for `bearertoken_id`.
        """
        pass

    def commit(self):
        url = 'http://192.168.1.76:8983/solr/dropbox/update'
        xml_data = '<commit waitSearcher="true" expungeDeletes="false"/>'.encode('utf-8')
        headers = {
            'Content-type': 'text/xml; charset=utf-8',
            'Content-Length': "%s" % len(xml_data)
        }
        r = requests.post(url, data=xml_data, headers=headers)
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

