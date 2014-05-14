import requests
import json
from os.path import join, normpath, splitext, basename
import logging

from utils.exceptions import SolrResponseError
from utils.dates import dropbox_date_to_solr_date
from magpie.settings import settings
from models import Provider
from utils.solr import escape_solr_query


log = logging.getLogger('dropbox')


class DropboxSolrUpdater:
    CORE_NAME = settings.CORE_NAMES[Provider.NAME_DROPBOX]

    def __init__(self, bearertoken_id):
        self.bearertoken_id = bearertoken_id
        self.url = '{}/{}/update'.format(settings.SOLR_URL, self.CORE_NAME)

    def add(self, redis_entry, commit=False):
        """
        Add a new file to the Solr index for the current `bearertoken_id`.

        Parameters:
        redis_entry -- a `RedisDropboxEntry` instance.
        """
        local_file_path = normpath(join(settings.DROPBOX_TEMP_STORAGE_PATH,
                                        str(self.bearertoken_id),
                                        redis_entry.local_name))

        # Build Solr doc.
        doc = self._convert_redis_entry_to_solr_doc(redis_entry, local_file_path)
        self._post_file(doc, local_file_path)

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
        doc['literal.id'] = '{}:{}'.format(self.bearertoken_id, redis_entry.id)
        doc['literal.remote_path'] = metadata['path']
        doc['literal.modified_at'] = dropbox_date_to_solr_date(metadata['modified'])
        doc['literal.mime_type'] = metadata['mime_type']
        doc['literal.bytes'] = metadata['bytes']

        return doc

    def delete(self, redis_entry, commit=False):
        """
        Delete a Dropbox file from the Solr index for the current `bearertoken_id`.

        Parameters:
        redis_entry -- a `RedisDropboxEntry` instance.
        """

        # We want to delete the specific entry and all its children, in case of any.
        # Note: '/' is a keyword in Solr, so we need to escape it this way: '\/'.
        # Note: keep in mind that there is no way to know if the entry is a folder or a file (cause
        # as this is a entry to delete, Dropbox doesn't send us metadata, and we cannot check
        # what is already in our index, because we don't index folders). But this is not a problem.
        #
        # First we delete the item: remote_path:\/folder1\/folder2\/folder\ 3
        # Then all children, if any: remote_path:\/folder1\/folder2\/folder\ 3\/*
        # Or all together:
        #   remote_path:(\/folder1\/folder2\/folder\ 3 OR \/folder1\/folder2\/folder\ 3\/*)
        #
        # Note: this is smart because we don't delete: /folder1/folder2/folder 30
        root = escape_solr_query(redis_entry.remote_path)
        children = '{}\/*'.format(root)
        q = 'remote_path_ci:({} OR {}) '.format(root.lower(), children.lower()) + \
            'AND bearertoken_id:{}'.format(self.bearertoken_id)
        self._delete_by_query(q)

        if commit:
            self.commit()

    def reset(self, commit=False):
        """
        Delete all files from the Solr index for the current `bearertoken_id`.
        """
        q = 'bearertoken_id:{}'.format(self.bearertoken_id)
        self._delete_by_query(q)

        if commit:
            self.commit()

    def commit(self):
        xml_data = '<commit waitSearcher="true" expungeDeletes="false"/>'
        r = self._post_xml(xml_data)
        self._sanity_check(r, False)

    def _delete_by_query(self, query):
        xml_data = '<delete><query>{}</query></delete>'.format(query)
        r = self._post_xml(xml_data)
        self._sanity_check(r)

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
        # Normally we would use the following dictionary to attach a file to a `requests.post`:
        #files = {'file': open(local_file_path, 'rb')}
        # But this would fail silently when the file name contains special chars (like
        # Chinese chars). The failure is subtle because the `requests.post` does not raise
        # any exception, it just posts no file at all.
        # To solve this we need to assign a fake name to the file.
        ext = splitext(basename(local_file_path))[1]  # Get the extension of the original file.
        # This way the posted file will be named: doc`.ext`.
        files = {'doc': ('doc' + ext, open(local_file_path, 'rb'))}
        log.debug('Posting file to Solr: {}'.format(self.url) +
                  '\nParams: {}'.format(params) +
                  '\nFile: {}'.format(local_file_path))
        # Send request.
        r = requests.post('{}/extract'.format(self.url), params=params, files=files)
        self._sanity_check(r)

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
        params = dict()
        params['wt'] = 'json'
        r = requests.post(self.url, params=params, data=xml_data, headers=headers)
        return r

    @staticmethod
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
                solr_status, json.dumps(json.loads(r.text), indent=4))
            )