from internetarchive import get_session
import argparse
import csv
import os
import shutil
import datetime
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

# get row count
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    rowCount = len(list(reader))

# create log
f = csv.writer(open('recordsUpdated.csv', 'w'))
f.writerow(['iaID'] + ['oclcNum'] + ['response'] + [''])

# script content
backupDirectory = 'archive.orgBackup/'
replacementDirectory = 'oclcRecords/'
if os.path.isdir(backupDirectory) is False:
    os.makedirs(backupDirectory)
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
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
        utc = datetime.datetime.utcnow()
        utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        f.writerow([iaId] + [oclcNum] + [r2] + [utcTime])
        print(r2)
