import json
from os.path import join, normpath
import logging

from utils.dates import dropbox_date_to_solr_date
from magpie.settings import settings
from models import Provider
import utils.solr
import utils.filesystem


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
        log.debug('Posting file to Solr: {}'.format(self.url) +
                  '\nDoc: {}'.format(doc) +
                  '\nFile: {}'.format(local_file_path))
        utils.solr.add_file(self.url, doc, local_file_path)
        utils.filesystem.remove(local_file_path)  # Delete the downloaded file.
        utils.filesystem.remove(local_file_path + '.metadata')  # Delete the metadata file.

        if commit:
            utils.solr.commit(self.url)

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
        root = utils.solr.escape_solr_query(redis_entry.remote_path)
        children = '{}\/*'.format(root)
        q = 'remote_path_ci:({} OR {}) '.format(root.lower(), children.lower()) + \
            'AND bearertoken_id:{}'.format(self.bearertoken_id)
        utils.solr.delete_by_query(self.url, q)

        if commit:
            utils.solr.commit(self.url)

    def reset(self, commit=False):
        """
        Delete all files from the Solr index for the current `bearertoken_id`.
        """
        q = 'bearertoken_id:{}'.format(self.bearertoken_id)
        utils.solr.delete_by_query(q)

        if commit:
            utils.solr.commit(self.url)