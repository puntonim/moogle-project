from utils.redis import RedisStore


class DropboxIndexer:
    """
    ...
    """

    def __init__(self, bearertoken_id, access_token):
        self.bearertoken_id = bearertoken_id
        self.access_token = access_token

    def run(self):
        """
        ....
        """
        redis_store = RedisStore(self.bearertoken_id)
        for redis_entry in redis_store.iter_over_index_list():
            print(redis_entry)

            # for each +, tells solr to index the local file
            # for each -, deletes the record from Solr (name and name/*)
