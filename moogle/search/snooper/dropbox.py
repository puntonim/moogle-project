from ..snooper import BaseSolrSnooper
from tokens.models import Provider


class DropboxSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_DROPBOX
        self.extra_query_args = {
            'fl': 'id,title,bytes,mime_type,content_type,remote_path,modified_at,'}