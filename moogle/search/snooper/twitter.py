from ..snooper import BaseSolrSnooper
from tokens.models import Provider


class TwitterSnooper(BaseSolrSnooper):
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_TWITTER