import argparse

from models import Provider
from utils.solr import Solr, CORE_NAMES


def syncdb(args):
    print("Creating the db...")
    from utils.db import setup_db
    setup_db()
    print("Done.")


def loaddata(args):
    print("Loading fixture into the database...")
    from utils.db import loaddata
    import json
    content = json.loads(args.file.read())
    loaddata(content)
    print("Done.")


def shell(args):
    print("Opening a shell and importing all models...")
    from utils.db import Session, get_all_models_classes

    # Import all models
    models_names = []
    for cls in get_all_models_classes():
        model_name = cls.__name__
        models_names.append(model_name)
        globals()[model_name] = getattr(
            __import__('models', fromlist=[model_name]), model_name)

    # Create a new session
    sex = Session()

    # Print some info
    print('')
    print("The following models have been loaded:\n{}".format(models_names))
    print("A session has been open with name `sex`.")
    print("You can run a query like:\n    sex.query({}).all()".format(models_names[0]))
    print('')

    # Start a debug session
    # Try import bpdb (which requires Bpython), if not import plain pdb
    try:
        import bpdb as debug
        # This is a trick to manually import the models because the automatic import of all
        # models works in pdb, but not in bpdb.
        from models import Provider, BearerToken
    except:
        import pdb as debug
    debug.set_trace()
    print("Done.")


def solr_reset(args):
    from utils.db import session_autocommit
    from models import BearerToken
    from sqlalchemy.orm.exc import NoResultFound

    if args.bearertoken_id:
        print(" * Resetting the Solr index for bearertoken_id: {}".format(args.bearertoken_id))

        with session_autocommit() as sex:
            try:
                bearertoken = sex.query(BearerToken).filter_by(id=args.bearertoken_id).one()
            except NoResultFound:
                print('There is no bearertoken_id {} in the database.'.format(args.bearertoken_id))
                return
            provider_name = bearertoken.provider.name
        query = 'bearertoken_id:{}'.format(args.bearertoken_id)

    if args.provider:
        print(" * Resetting the Solr index for provider: {}".format(args.provider))
        provider_name = args.provider
        query = '*:*'

    solr = Solr(CORE_NAMES[provider_name])
    solr.delete_by_query(query)
    solr.commit()
    print("Done.")


def solr_print(args):
    from utils.db import session_autocommit
    from models import BearerToken
    from sqlalchemy.orm.exc import NoResultFound

    if args.bearertoken_id:
        print(" * Printing the content of the Solr index for bearertoken_id: {}".format(
            args.bearertoken_id))

        with session_autocommit() as sex:
            try:
                bearertoken = sex.query(BearerToken).filter_by(id=args.bearertoken_id).one()
            except NoResultFound:
                print('There is no bearertoken_id {} in the database.'.format(args.bearertoken_id))
                return
            provider_name = bearertoken.provider.name
        query = 'bearertoken_id:{}'.format(args.bearertoken_id)

    if args.provider:
        print(" * Printing the Solr index for provider: {}".format(args.provider))
        provider_name = args.provider
        query = '*:*'

    solr = Solr(CORE_NAMES[provider_name])
    r = solr.search(q=query)
    for doc in r.documents:
        del doc['content']
        print(doc)

    print("\n * {} documents.".format(r.total_results))
    print("Done.")


def redis_flush(args):
    print("Flushing Redis keys...")
    from utils.redis import open_redis_connection
    redis = open_redis_connection()
    redis.flushall()
    print('Done.')


def redis_print(args):
    from utils.redis import open_redis_connection
    redis = open_redis_connection()

    if args.bearertoken_id:
        print("Printing Redis keys for bearertoken_id: {}.".format(args.bearertoken_id))
        lists = redis.keys('*token:{}'.format(args.bearertoken_id))
        if not lists:
            sizel = 0
            print("\n * NO LIST")
        # It should be only one list, but you never know...
        for list in lists:
            items = redis.lrange(list, 0 , -1)
            sizel = len(items)
            print("\n * THE LIST {} CONTAINS {} ITEMS:".format(list, sizel))
            print(items)

        hashes = redis.keys('*token:{}:*'.format(args.bearertoken_id))
        if not hashes:
            print("\n * NO HASHES")
        else:
            print("\n * THE HASHES ARE:")
        for hash_ in hashes:
            print(redis.hgetall(hash_))

        print("\n * CHECKS:")
        # Check that there is only 1 list like: *token:x
        size = len(lists)
        msg = 'OK' if size in [1, 0] else 'NOK!!!!!'
        print("{} list(s) found - {}".format(size, msg))
        # Check that the size of the list is = the number of hashes like *token:x:*
        sizeh = len(hashes)
        msg = 'OK' if sizel == sizeh else 'NOK!!!!!'
        print("{} items in the list, {} hashes - {}".format(sizel, sizeh, msg))

    if args.all:
        print(" * PRINTING ALL REDIS KEYS:")
        keys = redis.keys('*')
        for key in keys:
            print(key.decode('utf-8'))
        print("\n * {} KEYS FOUND".format(len(keys)))

    print('\nDone.')


def update(args):
    from updater import UpdateManager

    bearertoken_id = args.bearertoken_id
    if args.test_bearertoken_id:
        if args.test_bearertoken_id == 'facebook':
            bearertoken_id = '49'
        elif args.test_bearertoken_id == 'twitter':
            bearertoken_id = '48'
        elif args.test_bearertoken_id == 'dropbox':
            bearertoken_id = '46'
    print("Fetching updates for bearertoken_id: {}".format(bearertoken_id))
    updater = UpdateManager(bearertoken_id, args.reset_cursor)
    updater.run()

    print("Done.")


def ping(args):
    print('Ping... pong')
    print("Done.")


if __name__ == '__main__':
    provider_names = list(Provider.NAME_CHOICES)
    provider_names.append('all')

    parser = argparse.ArgumentParser(description="Run magpie commands.")
    subparsers = parser.add_subparsers()

    # `syncdb` subcommand.
    subcmd = subparsers.add_parser('syncdb', help='Create the database.')
    subcmd.set_defaults(func=syncdb)

    # `shell` subcommand.
    subcmd = subparsers.add_parser('shell', help='Open a Python shell with all models imported.')
    subcmd.set_defaults(func=shell)

    # `redis` subcommand.
    subcmd = subparsers.add_parser('redis', help='Flush and print operations on Redis.')
    sub_subparsers = subcmd.add_subparsers()
    # `redis flushall` sub-subcommand.
    sub_subcmd = sub_subparsers.add_parser('flushall', help='Flush all keys in Redis.')
    sub_subcmd.set_defaults(func=redis_flush)
    # `redis print` sub-subcommand.
    sub_subcmd = sub_subparsers.add_parser('print', help='Print keys in Redis.')
    group = sub_subcmd.add_mutually_exclusive_group(required=True)
    group.add_argument('--bearertoken_id', type=int,
                        help='The bearertoken_id to print Redis keys for.')
    group.add_argument('--all', action='store_true',
                       help='All keys.')
    sub_subcmd.set_defaults(func=redis_print)

    # `loaddata` subcommand.
    subcmd = subparsers.add_parser('loaddata', help='Load a json fixture.')
    subcmd.add_argument('file', type=argparse.FileType('r'),
                        help='Path to the json fixture file.')
    subcmd.set_defaults(func=loaddata)

    # `update` subcommand.
    subcmd = subparsers.add_parser('update', help='Fetch updates for a bearertoken_id.')
    group = subcmd.add_mutually_exclusive_group(required=True)
    group.add_argument('--bearertoken-id', type=int,
                        help='The bearertoken_id to fetch updates for.')
    group.add_argument('--test-bearertoken-id', choices=Provider.NAME_CHOICES,
                        help='Use the test bearertoken_id for the given provider.')
    subcmd.add_argument('--reset-cursor', action='store_true',
                        help='Reset the cursor before updating.')
    subcmd.set_defaults(func=update)

    # `solr` subcommand.
    subcmd = subparsers.add_parser('solr', help='Reset and print the content of Solr index.')
    sub_subparsers = subcmd.add_subparsers()
    # `solr reset` sub-subcommand.
    sub_subcmd = sub_subparsers.add_parser('reset', help='Reset Solr index.')
    group = sub_subcmd.add_mutually_exclusive_group(required=True)
    group.add_argument('--bearertoken_id', type=int,
                        help='The bearertoken_id to reset the Solr index for.')
    group.add_argument('--provider', choices=CORE_NAMES.values(),
                       help='The provider (Solr core) to reset.')
    sub_subcmd.set_defaults(func=solr_reset)
    # `solr print` sub-subcommand.
    sub_subcmd = sub_subparsers.add_parser('print', help='Print Solr index.')
    group = sub_subcmd.add_mutually_exclusive_group(required=True)
    group.add_argument('--bearertoken_id', type=int,
                        help='The bearertoken_id to print the Solr index for.')
    group.add_argument('--provider', choices=CORE_NAMES.values(),
                       help='The provider (Solr core) to print.')
    sub_subcmd.set_defaults(func=solr_print)

    # `ping` subcommand -- just a mock.
    subcmd = subparsers.add_parser('ping', help='Prints pong.')
    subcmd.set_defaults(func=ping)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()