from internetarchive import get_session
import argparse
import csv
import os
import shutil
import secrets

# command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName', help='the file of data to be searched. \
optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the file of data to be searched: ')

# archive.org authentication
c = {'s3': {'access': secrets.access, 'secret': secrets.secret}}
s = get_session(config=c)

with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    rowCount = len(list(reader))

# script content
backupDirectory = 'archive.orgBackup/'
replacementDirectory = 'oclcRecords/'
if os.path.isdir(replacementDirectory) is False:
    os.makedirs(replacementDirectory)
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if rowCount == 101:
            rowCount -= 1
            print('Items remaining: ', rowCount)
            iaId = row['iaIdentifier']
            oclcNum = row['oclcNum']
            item = s.get_item(iaId)
            fileName = iaId + '_marc.xml'
            r = item.download(files=fileName, destdir=backupDirectory)
            print(r)
            print(oclcNum + '.xml', iaId + '_marc.xml')
            shutil.copy(replacementDirectory + oclcNum + '.xml',
                        replacementDirectory + iaId + '_marc.xml')
            r2 = item.upload(replacementDirectory + iaId + '_marc.xml')
            print(r2)

# id = 'mit_pub_dom_test_object1'
# id = 'preludeno2furios00jaco'
# item = s.get_item(id)
# r = item.upload(id + '_marc.xml')
# print(r)
# title = item.item_metadata['metadata']['title']
# print(title, item.item_metadata)

# item = s.get_item('mit_pub_dom_test_object')
# print(item.metadata['curation'])
# print(item.item_metadata)
