import json
from os import mkdir
from os.path import exists, join, normpath, split

from dropbox.client import DropboxClient

from .dbutils import session_autocommit
from magpie.settings import settings


class DropboxCrawler:
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    @property
    def _client(self):
        try:
            cl = self._client_cached
        except AttributeError:
            cl = self._client_cached = DropboxClient(self.bearertoken.access_token)
        return cl


    def update_index(self):
        with session_autocommit() as sex:
            # Add bearertoken to the current session
            self.bearertoken = sex.merge(self.bearertoken)

            print("VAIIII", self.bearertoken, self.bearertoken.access_token, self._client)

            #TODO remove the prefix once ready
            ___PATH_PREFIX='/temp/moogletest'
            # TODO catch the exception dropbox.rest.ErrorResponse: [401] "The given OAuth 2
            # access token doesn't exist or has expired."
            r = self._client.delta(cursor=self.bearertoken.updates_cursor,
                                   path_prefix=___PATH_PREFIX)
            # `r` is now a python dictionary representing the response to a delta call (see
            # docstring in DropboxDeltaParser for an example

            # Initialize the parser and the Solr Updater
            parser = DropboxDeltaParser(r)

            # TODO debug stuff
            print("# ENTRIES: {}".format(len(r.get('entries'))))
            print("HAS MORE: {}".format(parser.has_more))
            print("RESET: {}".format(parser.reset))
            print("CURSOR: {}".format(parser.cursor))
            print("NEW\n{}".format('\n'.join(parser.new_entries)))
            print("DELETED:\n{}".format('\n'.join(parser.deleted_entries)))
            #print( json.dumps(r.json(), indent=4) )

            # Save the new cursor
            self.bearertoken.updates_cursor = parser.cursor
            sex.commit()

            solr = DropboxSolrUpdater(self._client)
            # Reset the user's Solr index
            if parser.reset:
                solr.reset()

            solr.update(parser.new_entries)
            solr.delete(parser.deleted_entries)

            has_more = parser.has_more

            # Save memory
            del r  # r can be big
            del parser
            del solr

            # TODO if parser.has_more devo rilanciare la stessa chiamata
            # TODO potenziale problema di prestazioni, se sto analizzando una cartella con migliai di file allora
            # ci sara' l'has_more e il risultato finale sara un grande insieme new_items
            # Ho fatto dei test e mi ha mandato un has more con 941 elementi, quindi sembra che il limite sia vicino a mille
            # Potenziali soluz: ad ogni ciclo processo i dizionari, poi richiamo delta x avere i succesivi, pero sul sito
            # c'e' scritto " you can call /delta again immediately to retrieve those entries. If 'false', then wait for at
            # least five minutes (preferably longer) before checking again." quindi nn so se devo sbrigarmela con queste
            # chiamate. da testare
            if has_more:
                self.update_index()


class DropboxDeltaParser():
    """
        ...
        requests.models.Response
        Example fo response:
        {
            "cursor": "AAFP6m8ToJqE7ULQgwicDOZGmCHs2eiadgsBOxU9vIpdzu4W7rWVn8oQFo_jCIOuDp8txUNVHhxkfnsV5bIgBALHh8hK6KGcWFNPgoQGTPT02DL7El_XBvl6j7GszfGLrhYbnE3pV0Zzzk9ObQOfppF_6awSxjJBgNY7qD3VOKgfxA",
            "has_more": false,
            "reset": true,
            "entries": [
                [
                    "/temp/moogletest",
                    {
                        "bytes": 0,
                        "revision": 241716,
                        "modified": "Mon, 27 Jan 2014 20:17:24 +0000",
                        "size": "0 bytes",
                        "root": "dropbox",
                        "is_dir": true,
                        "thumb_exists": false,
                        "path": "/temp/moogletest",
                        "rev": "3b0340265d3a0",
                        "icon": "folder"
                    }
                ],
                [
                    "/temp/moogletest/uno.txt",
                    {
                        "mime_type": "text/plain",
                        "bytes": 205,
                        "thumb_exists": false,
                        "modified": "Mon, 27 Jan 2014 21:09:36 +0000",
                        "size": "205 bytes",
                        "path": "/temp/moogletest/uno.txt",
                        "icon": "page_white_text",
                        "client_mtime": "Wed, 14 Mar 2012 00:02:51 +0000",
                        "root": "dropbox",
                        "is_dir": false,
                        "revision": 241780,
                        "rev": "3b0740265d3a0"
                    }
                ],
                [
                    "/temp/moogletest/tre",
                    {
                        "bytes": 0,
                        "revision": 242348,
                        "modified": "Tue, 28 Jan 2014 16:08:52 +0000",
                        "size": "0 bytes",
                        "root": "dropbox",
                        "is_dir": true,
                        "thumb_exists": false,
                        "path": "/temp/moogletest/tre",
                        "rev": "3b2ac0265d3a0",
                        "icon": "folder"
                    }
                ],
                [
                    "/temp/moogletest/tre/myfile.txt",
                    null
                ],
                [
                    "/temp/moogletest/tre/quattro.txt",
                    {
                        "mime_type": "text/plain",
                        "bytes": 205,
                        "thumb_exists": false,
                        "modified": "Tue, 28 Jan 2014 16:08:59 +0000",
                        "size": "205 bytes",
                        "path": "/temp/moogletest/tre/quattro.txt",
                        "icon": "page_white_text",
                        "client_mtime": "Wed, 14 Mar 2012 00:02:51 +0000",
                        "root": "dropbox",
                        "is_dir": false,
                        "revision": 242351,
                        "rev": "3b2af0265d3a0"
                    }
                ]
            ]
        }
    """

    def __init__(self, response):
        self.r = response

    @property
    def cursor(self):
        return self.r.get('cursor', '')

    @property
    def reset(self):
        return self.r.get('reset', False)

    @property
    def has_more(self):
        return self.r.get('has_more', False)

    @property
    def new_entries(self):
        if not hasattr(self, '_new_entries'):
            self._parse_entries()
        return self._new_entries

    @property
    def deleted_entries(self):
        if not hasattr(self, '_deleted_entries'):
            self._parse_entries()
        return self._deleted_entries

    def _parse_entries(self):
        """
        Parse all entries and add them to a dictionary where:
            key = file path (lower case, but dropbox is case insensitive)
            value = operation ('+' for adding/editing, '-' for deleting if existent)
        In case there are multiple operation on the same file, only the most recent operation is kept, due to
        the nature of the dictionary (keys are unique): this is exactly what we want
        When the parsing is done, the final dictionary is split into 2 lists based on the operation:
         _new_entries and _deleted_entries
        """
        # Dictionary with all the operations to perform, we don't need an OrderedDict because in
        # case there are multiple operation on the same file, only the most recent operation is
        # kept, due to the nature of the dictionary (keys are unique): this is exactly what we want
        ops = dict()
        for entry in self.r.get('entries', list()):
            # item is a list like this:
            # ]
            #    "/temp/moogletest/tre/myfile.txt",
            #    {
            #        "revision": 242622,
            #        "rev": "3b3be0265d3a0",
            #        "modified": "Wed, 29 Jan 2014 08:39:54 +0000",
            #        "path": "/temp/moogletest/tre/Myfile.txt",
            #        "bytes": 205,
            #        "thumb_exists": false,
            #        "is_dir": false,
            #        "size": "205 bytes",
            #        "client_mtime": "Wed, 14 Mar 2012 00:02:51 +0000",
            #        "mime_type": "text/plain",
            #        "root": "dropbox",
            #        "icon": "page_white_text"
            #    }
            # ]
            # or:
            # [
            #        "/temp/moogletest/tre/myfile.txt",
            #        null
            # ]
            #

            # Checks on the consistency of entry
            if not len(entry) == 2:
                # TODO log this
                continue

            path = entry[0]
            metadata = entry[1]

            # Check weather path is not '' and is a string
            if not path or not isinstance(path, str):
                continue

            # If there is no metadata it is a file to delete
            if not metadata:
                ops[path] = '-'
                continue

            # If there is a metadata
            #   and it is not a dir (so it's a file)
            #   and its size is allowed
            # then it is a file to add
            try:
                is_dir = metadata['is_dir']
                size = metadata['bytes']
            except KeyError:
                # If those key are not present, skip it
                # TODO log these errors
                continue
            if not is_dir and size <= settings.DROPBOX_MAX_FILE_SIZE:
                ops[path] = '+'

        # Now op is a dict with all the operations to performs. There is only one entry per path
        # (the most recent operation), which means that the intersection between the 2 lists
        # (_new_entries and _deleted_entries) is empty.
        # Split op in 2 lists: _new_entries and _deleted_entries
        self._new_entries = list()
        self._deleted_entries = list()
        if not ops:
            # TODO log it
            return
        # Destructively iterate over a dictionary (it's for performance issue cause op can be a
        # huge dict)
        for path, operation in list(ops.items()):
            if operation == '+':
                self._new_entries.append(path)
            else:
                self._deleted_entries.append(path)
            del ops[path]


class DropboxSolrUpdater:
    """
    Update Solr by adding and deleting entries.

    Parameters:
    bearertoken -- The bearertoken for the `Provider` we are indexing.
    client -- Optional :class:`dropbox.client.DropboxClient` object to use to query Dropbox's API
    service. If not provided it is built from the given user.
    """

    def __init__(self, client):
        self.client = client
        self.bearertoken = 'my_bearertoken'  # TODO read it from client or add it as __init__ param

    def update(self, entries):
        """
        Update the Solr index of the given user by adding new entries. Each one of the given entries is downloaded
        from Dropbox and its content added to the Solr index of the the given user. If the entry already exists
        in Solr it is updated.

        Parameters
            entries
             A list of paths describing resources (files). Only files with text content are accepted, not folder. It
             does NOT make sense to add to Solr folders or no-text files. Each item of the list is the actual local
             path at Dropbox side. We download that file and pass it to Solr.
        """

        # Note: ENTRIES IS A LIST OF FILES, NO FOLDERS! Because folders have been filtered out by previous processing
        #
        # We download files and their metadata. We store any file downloaded from Dropbox in a special folder. Inside
        # this folder we create a folder with name = user.id. Inside this user folder we store its files.
        # The original file name is kept when possible, but not the original path: so there is no subfolder inside
        # the user folder. If it is not possible to keep the original file name (because there is already a file with
        # the same name) then we change the name to something random (e.g. we add a number).
        # Metadata are stored in a file with the same name as the original file and with extension ".metadata"
        #
        # Why do we need the metadata? First reading the info in the metadata is the only way to know the original
        # path of the file at Dropbox side
        # plus keep in mind that "Dropbox treats file names in a case-insensitive but case-preserving way. To
        # facilitate this, the path strings above are lower-cased versions of the actual path. The metadata dicts
        # have the original, case-preserved path."
        # https://www.dropbox.com/developers/core/docs/python#DropboxClient (see delta() method)
        # This means that the identifier (entry in this case) is lower case but the real case sensitive name is
        # written in the metadata. This is another reason we might need metadata.

        def _get_valid_file_name(entry):
            """Closure to create a valid file name for the current entry"""
            # Create user folder inside the dropbox temp repo folder
            # TODO: change AAA to something unique for this bearertoken (e.g. bearertoken.uid)
            local_folder = normpath(join(settings.DROPBOX_TEMP_REPO_PATH, 'aaa'))
            if not exists(local_folder):
                mkdir(local_folder)

            # entry is a file so it must not end with a '/'
            assert not entry.endswith('/')  # otherwise this will compromise the os.split

            # Split a path in a tuple: (until last '/' excluded, after last '/' excluded)
            _, file_name = split(entry)
            local_file_path = normpath(join(local_folder, file_name))

            # We put all files in a single folder, we don't recreate the entire folders structure
            # of a user's dropbox account; so there can be file name clashes.
            # Thus we have to get an available local file name by appending a number to the end
            # of the filename.
            i = ''
            while exists(local_file_path + str(i)):
                if i == '':
                    i = 0
                else:
                    i += 1
            return local_file_path + str(i)

        # Download files from Dropbox and store them locally
        for entry in entries:
            local_file_path = _get_valid_file_name(entry)
            # Download the file. We could use client.get_file or client.get_file_and_metadata, but under the hood the
            # actual call to the API is the same, cause that API call returns the file plus its metadata
            f, metadata = self.client.get_file_and_metadata(entry)
            with f, open(local_file_path, 'wb') as fout, open(local_file_path+".metadata", 'w') as metaout:
                # TODO shall we read chunk by chunk and write it? Do we have performance issue fi the file is 10MB?
                fout.write(f.read())
                metaout.write(json.dumps(metadata, indent=4))
            #TODO now somehow notify solr that a new file has been added, so solr can take it and then delete it


    def delete(self, entries):
        """
        Delete entries from the Solr index of the given user.

        Parameters
            entries
             A list of paths describing resources (files or folders). If the resource if a folder its content is
             deleted (keep in mind that Solr doesn't index folders but only files with textual content). Each item of
             the list is the actual local path at Dropbox side.
        """
        # Note: ENTRIES IS A LIST OF FILES AND FOLDERS! Because it was NOT possible to filter out folders during the
        # previous processing
        #
        # Dropbox says: "... delete whatever is at path, including any children (you will sometimes also get "delete"
        # delta entries for the children, but this is not guaranteed)"
        # https://www.dropbox.com/developers/core/docs/python#DropboxClient (see delta() method)
        # This means that if the resource is:
        #   a file: we need to delete the solr index for this file
        #   a folder: we need to delete the solr index of the files children of this folder (keep in mind that Solr
        #             doesn't index folders)'
        # Plus there is no way to guess if the resource is a file or a folder. There is no metadata together with the
        # file/folder (because a deletion in Dropbox is identified right by the fact that there is no metadata).
        # Plus again Solr doesn't index folder, so we cannot query Solr to see if the entry is a file or a folder.
        # We can solve by simply deleting the resource itself (if existent) and all the other resources starting
        # with resource + '/'
        #
        # E.g. resource to delete: /documents/school/math
        # It can be a file with no extension or a folder - we don't know
        # We ask Solr to delete:
        #   the item itself (if existent): /documents/school/math
        #   any other existent item starting with: /documents/school/math/
        for entry in entries:
            print("Send a msg to Solr to delete:\n"
                  "  - the entry (if existent): {}\n"
                  "  - all the entries starting with: {}/\n"
                  "  - owned by the bearertoken: {}".format(entry, entry, self.bearertoken))

    def reset(self):
        """
        Reset the entire Solr index for the given user.
        """
        print("Send a msg to Solr to delete the entire index for the bearertooen: {}".format(self.bearertoken))