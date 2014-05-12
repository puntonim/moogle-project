from os.path import join, normpath, dirname, realpath, split
import hashlib
from collections import Counter
from utils.solr import open_solr_connection

from dropboxlib.indexer.solrupdater import DropboxSolrUpdater


class SolrUtils:

    def add(self):
        bearertoken_id = '88888888xxx'
        solr = DropboxSolrUpdater(bearertoken_id)

        # Path to alice.txt
        local_file_path = normpath(join(dirname(realpath(__file__)), 'alice.txt'))

        # Build Solr doc.
        # Add doc.
        doc = dict()
        doc['literal.bearertoken_id'] = bearertoken_id
        id = bearertoken_id + ':' + hashlib.md5('/////'.encode()).hexdigest()
        doc['literal.id'] = id + '-1'
        doc['literal.remote_path'] = '/folder1/file1.txt'
        doc['literal.modified_at'] = '2014-05-07T10:00:54Z'
        doc['literal.mime_type'] = 'text/plain'
        doc['literal.bytes'] = '345'

        solr = DropboxSolrUpdater(bearertoken_id)
        local_file_path = normpath(join(dirname(realpath(__file__)), 'alice.txt'))
        solr._post_file(doc, local_file_path)

        solr.commit()


    def get_remote_paths(self, bearertoken_id):
        solr = open_solr_connection('dropbox')
        q = '*'
        fq = 'bearertoken_id:4'
        fl = 'remote_path'
        start = 0
        rows = 1000
        r = solr.search(q=q, fq=fq, fl=fl, start=start, rows=rows)
        remote_paths = list()
        for doc in r.documents:
            remote_paths.append(doc['remote_path'])
        return remote_paths


    def draw_tree(self, source):
        """
        Very ugly method to print a tree of files.
        """
        tree_dict = dict()
        for root in source:
            dir_path, file_name = split(root)
            i = tree_dict.get(dir_path, [0, []])
            i[0] = Counter(dir_path)['/']
            i[1].append(file_name)
            tree_dict[dir_path] = i

        root = tree_dict.get('/', None)
        if root:
            del tree_dict['/']
            print('/')
            spaces = ' ' * 4
            for file in root[1]:
                print('{}{}'.format(spaces, file))

        i = 1
        while True:
            to_del = []
            for k, v in tree_dict.items():
                if v[0] == i:
                    spaces = ' ' * 4 * i
                    print('{}{}/'.format(spaces, k))
                    to_del.append(k)
                    spaces = ' ' * 4 * (i+1)
                    for file in v[1]:
                        print('{}{}'.format(spaces, file))

            i += 1
            for el in to_del:
                del tree_dict[el]
            if tree_dict:
                continue
            break



if __name__ == '__main__':
    #solr = SolrUtils()
    #solr.add()

    solr = SolrUtils()
    remote_paths = solr.get_remote_paths('4')
    solr.draw_tree(remote_paths)