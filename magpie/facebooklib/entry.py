from abc import ABCMeta


class AbstractFacebookEntry(metaclass=ABCMeta):
    id = ''
    from_name = ''
    from_id = ''
    type = ''
    created_time = ''
    updated_time = ''
    message = ''


class ApiFacebookEntry(AbstractFacebookEntry):
    """
    A post (status, link, photo or video) got in a reply to a API query.

    Parameters:
    facebook_dict -- a Python dictionary like:
        {
            'id': '1522956429_10204108119132902',
            'from': {
                'name': 'Paulo Van Der Kofje',
                'id': '1522956429'
            },
            'type': 'status',
            'created_time': '2014-05-01T16:59:41+0000',
            'updated_time': '2014-05-01T16:59:41+0000',
            'message': 'test message'
        }
    """

    def __init__(self, post_dict):
        self.id = post_dict['id']
        self.from_name = post_dict['from']['name']
        self.from_id = post_dict['from']['id']
        self.type = post_dict['type']
        self.created_time = post_dict['created_time']
        self.updated_time = post_dict['updated_time']
        # Message can be missing in facebook_dict (f.i. for a link or photo w/ no message).
        self.message = post_dict.get('message', '')


class RedisFacebookEntry(AbstractFacebookEntry):
    """
    A post (status, link, photo or video) stored in Redis.

    Parameters:
    post_id -- a string, the id of the Facebook post.
    post_dict -- a Python dictionary like:
        {
            b'from_name': 'Paulo Van Der Kofje',
            b'from_id': '1522956429',
            b'type': 'status',
            b'created_time': '2014-05-01T16:59:41+0000',
            b'updated_time': '2014-05-01T16:59:41+0000',
            b'message': 'test message'
        }
    """
    def __init__(self, post_id, post_dict):
        self.id = post_id.decode(encoding='UTF-8')
        self.from_name = post_dict[b'from_name'].decode(encoding='UTF-8')
        self.from_id = post_dict[b'from_id'].decode(encoding='UTF-8')
        self.type = post_dict[b'type'].decode(encoding='UTF-8')
        self.created_time = post_dict[b'created_time'].decode(encoding='UTF-8')
        self.updated_time = post_dict[b'updated_time'].decode(encoding='UTF-8')
        self.message = post_dict[b'message'].decode(encoding='UTF-8')