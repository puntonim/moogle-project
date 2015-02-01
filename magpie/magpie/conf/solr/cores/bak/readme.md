- Download solr from:
http://lucene.apache.org/solr/downloads.html

- Extract the archive in the folder solr-4.10.3:
tar -xzvf solr-4.10.3.tgz

- Enter that folder and copy `example` to `moogle`:
cd solr-4.10.3
cp -R example moogle

- Enter moogle folder and delete the solr folder:
rm -rf solr

- Extract solr-empty.tar.gz in moogle/solr:
tar -xzvf solr-empty.tar.gz