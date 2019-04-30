from internetarchive import get_session
import argparse
import csv
import os
import shutil
import time
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

# archive.org authentication and start time
c = {'s3': {'access': secrets.access, 'secret': secrets.secret}}
s = get_session(config=c)
startTime = time.time()

# get row count
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    rowCount = len(list(reader))

# create log
currTime = datetime.datetime.utcnow()
logCreateTime = currTime.strftime('%Y-%m-%dT%H:%M:%SZ')
f = csv.writer(open('recordsUpdated' + logCreateTime + '.csv', 'w'))
f.writerow(['iaID'] + ['oclcNum'] + ['response'] + [''])

# script content
backupDirectory = 'archive.orgBackup/'
replacementDirectory = 'oclcRecords/'
if os.path.isdir(backupDirectory) is False:
    os.makedirs(backupDirectory)
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        iaId = row['iaIdentifier']
        oclcNum = row['oclcNum']
        item = s.get_item(iaId)
        fileName = iaId + '_marc.xml'
        r = item.download(files=fileName, destdir=backupDirectory)
        print(oclcNum + '.xml', iaId + '_marc.xml')
        shutil.copy(replacementDirectory + oclcNum + '.xml',
                    replacementDirectory + iaId + '_marc.xml')
        key = 'force-update'
        value = 'true'
        updateDict = {key: value}
        forceUpdate = item.modify_metadata(dict(updateDict))
        removeDesc = item.modify_metadata(dict(description='REMOVE_TAG'))
        removeSubj = item.modify_metadata(dict(subject='REMOVE_TAG'))
        uploadMarc = item.upload(replacementDirectory + iaId + '_marc.xml')
        utc = datetime.datetime.utcnow()
        utcTime = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        f.writerow([iaId] + [oclcNum] + [uploadMarc] + [utcTime])
        rowCount -= 1
        print('Items remaining: ', rowCount)
        print(uploadMarc)

# print script run time
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
