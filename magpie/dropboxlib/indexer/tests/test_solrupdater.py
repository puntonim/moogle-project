from unittest import TestCase
import warnings
import hashlib
from os.path import join, normpath, dirname, realpath
from unittest.mock import Mock

from utils.solr import open_solr_connection
from ..solrupdater import DropboxSolrUpdater


###################################################################################################
# NOTE: unit test must not depend on external resources like Solr
# We must use mocks here!
###################################################################################################


class DropboxSolrUpdaterTest(TestCase):

    # Called once before the class initialization. Exceptions here are real errors.
    # To use only for expensive elaboration.
    @classmethod
    def setUpClass(cls):
        # mysolr generates a warning like "ResourceWarning: unclosed <socket.socket object,".
        # We ignore this:
        # http://stackoverflow.com/questions/20885561/
        # warning-from-warnings-module-resourcewarning-unclosed-socket-socket-object
        warnings.simplefilter('ignore')

    # Called after all tests have run (successfully or not). Exceptions here are real errors.
    # Not called in case of errors in setUpClass().
    # To use only for expensive elaboration.
    @classmethod
    def tearDownClass(cls):
        pass

    # Called before each test. Exceptions here are real errors.
    # To use for code shared by all tests.
    def setUp(self):
        self.bearertoken_id = '7777777xxx'
        self.bearertoken_id2 = '7777777xxxy'
        self.reset()
        self.add_docs()

    # Called after each test (even if the test method raised an exception). Exceptions here
    # are real errors. Not called in case of errors in setUp(). If you need a clean up even
    # in case of errors in setUp(), then call self.addCleanup(function, *args, **kwargs)
    # within a test and it will run after that test (only that test).
    def tearDown(self):
        self.reset()

    def reset(self):
        solr = DropboxSolrUpdater(self.bearertoken_id)
        solr.reset()
        solr.commit()
        solr = DropboxSolrUpdater(self.bearertoken_id2)
        solr.reset()
        solr.commit()

    def add_docs(self):
        # Add doc.
        doc = dict()
        doc['literal.bearertoken_id'] = self.bearertoken_id
        id = self.bearertoken_id + ':' + hashlib.md5('/////'.encode()).hexdigest()
        doc['literal.id'] = id + '-1'
        doc['literal.remote_path'] = '/Folder1/file1'
        doc['literal.modified_at'] = '2014-05-07T10:00:54Z'
        doc['literal.mime_type'] = 'text/plain'
        doc['literal.bytes'] = '345'

        solr = DropboxSolrUpdater(self.bearertoken_id)
        local_file_path = normpath(join(dirname(realpath(__file__)), 'alice.txt'))
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-2'
        doc['literal.remote_path'] = '/Folder1/file2.txt'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-3'
        doc['literal.remote_path'] = '/Folder1/folder2/file1'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-4'
        doc['literal.remote_path'] = '/Folder1/folder2/folder1/'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-5'
        doc['literal.remote_path'] = '/Folder1/folder2/folder2/file1'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-6'
        doc['literal.remote_path'] = '/Folder1/folder2/folder2/file2.txt'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-7'
        doc['literal.remote_path'] = '/Folder1/folder2/file2'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-8'
        doc['literal.remote_path'] = '/Folder1/folder2/folder 3/file2.txt'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-9'
        doc['literal.remote_path'] = '/Folder1/folder2/folder 3/folder4/folder5/file6'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.id'] = id + '-10'
        doc['literal.remote_path'] = '/Folder1/folder2/folder 33'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.bearertoken_id'] = self.bearertoken_id2
        id = self.bearertoken_id2 + ':' + hashlib.md5('/////'.encode()).hexdigest()
        doc['literal.id'] = id + '-1'
        doc['literal.remote_path'] = '/Folder1/folder2/folder 3'
        solr._post_file(doc, local_file_path)

        # Add doc.
        doc['literal.bearertoken_id'] = self.bearertoken_id2
        doc['literal.id'] = id + '-2'
        doc['literal.remote_path'] = '/Folder1/folder2/folder 3/file'
        solr._post_file(doc, local_file_path)

        solr.commit()

    def get_number_of_docs(self, bearertoken_id):
        solr = open_solr_connection('dropbox')
        r = solr.search(q='bearertoken_id:{}'.format(bearertoken_id))
        return r.total_results

    def get_number_of_docs_for_query(self, **kwargs):
        solr = open_solr_connection('dropbox')
        r = solr.search(**kwargs)
        return r.total_results

    def test_reset(self):
        """
        The reset command deletes all docs for a specific beraretoken_id.
        """
        self.assertEqual(self.get_number_of_docs(self.bearertoken_id), 10)

        solr = DropboxSolrUpdater(self.bearertoken_id)
        solr.reset()  # The command under test.
        solr.commit()

        self.assertEqual(self.get_number_of_docs(self.bearertoken_id), 0)

    def test_delete(self):
        """
        The reset command deletes all docs for a specific beraretoken_id.
        """
        q = 'remote_path_ci:\/folder1\/folder2\/folder 3*'
        fq = 'bearertoken_id:{}'.format(self.bearertoken_id)
        self.assertEqual(self.get_number_of_docs_for_query(q=q, fq=fq), 3)

        solr = DropboxSolrUpdater(self.bearertoken_id)
        redis_entry = Mock()
        redis_entry.remote_path = '/Folder1/folder2/folder 3'
        solr.delete(redis_entry)  # The command under test.
        solr.commit()

        self.assertEqual(self.get_number_of_docs_for_query(q=q, fq=fq), 1)
        fq = 'bearertoken_id:{}'.format(self.bearertoken_id2)
        self.assertEqual(self.get_number_of_docs_for_query(q=q, fq=fq), 2)
