from unittest import TestCase

from utils.solr import open_solr_connection


class DropboxSolrUpdaterTest(TestCase):

    # Called once before the class initialization. Exceptions here are real errors.
    # To use only for expensive elaboration.
    @classmethod
    def setUpClass(cls):
        pass

    # Called after all tests have run (successfully or not). Exceptions here are real errors.
    # Not called in case of errors in setUpClass().
    # To use only for expensive elaboration.
    @classmethod
    def tearDownClass(cls):
        pass

    # Called before each test. Exceptions here are real errors.
    # To use for code shared by all tests.
    def setUp(self):
        pass

    # Called after each test (even if the test method raised an exception). Exceptions here
    # are real errors. Not called in case of errors in setUp(). If you need a clean up even
    # in case of errors in setUp(), then call self.addCleanup(function, *args, **kwargs)
    # within a test and it will run after that test (only that test).
    def tearDown(self):
        pass

    def test_reset(self):
        """
        A file written with the right content and metadata.
        """
        #self.solr.delete_by_query('bearertoken_id:13')
        #self.solr.commit()
        #solr = open_solr_connection('dropbox')
        #response = solr.search(q='*:*')
        from ..solrupdater import DropboxSolrUpdater
        solr = DropboxSolrUpdater('4')
        solr.reset()
        solr.commit()
        self.assertTrue(True)