from os.path import normpath, join, exists, split
from os import mkdir
from magpie.settings import settings


class DropboxFile:
    """
    A file to be downloaded in Dropbox.

    Parameters:
    content -- actual content of the file in a context manager (to be read with a with statement)
    metadata -- metadata describing the file. Example:
    {
        "revision": 241778,
        "thumb_exists": false,
        "size": "387.4 KB",
        "root": "dropbox",
        "bytes": 396682,
        "client_mtime": "Thu, 17 Jan 2013 17:59:14 +0000",
        "path": "/temp/moogletest/due.pdf",
        "rev": "3b0720265d3a0",
        "mime_type": "application/pdf",
        "is_dir": false,
        "icon": "page_white_acrobat",
        "modified": "Mon, 27 Jan 2014 21:09:33 +0000"
    }
    """

    def __init__(self, content, metadata):
        self.content = content
        self.metadata = metadata

    def store_to_disk(self, bearertoken_id):
        pass

    def _find_valid_local_name(self, bearertoken_id):
        """

        """
        # Create user folder inside DROPBOX_TEMP_REPO_PATH, named after the bearertoken_id.
        local_folder = normpath(join(settings.DROPBOX_TEMP_REPO_PATH, str(bearertoken_id)))
        if not exists(local_folder):
            mkdir(local_folder)

        # The remote file path is in metadata['path'].
        # metadata['path'] must exists otherwise it is a major issue.
        # It must be a file (we download only files, not folders) so it must not end with a '/'
        # otherwise this will compromise the os.split.
        try:
            remote_path = self.metadata['path']
            assert not remote_path.endswith('/')
        except (KeyError, AssertionError):
            pass

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