from __future__ import print_function, unicode_literals

from PyInquirer import prompt

from examples import custom_style_3
import time

from gDrive import *


def dontUseOldPath(answers):
    # demonstrate use of a function... here a lambda function would be enough
    return not answers['useOldPath']


def dontUseOldDrive(answers):
    # demonstrate use of a function... here a lambda function would be enough
    return not answers['useOldDrive']


questions = []

if not os.path.isfile('savedDrives.txt'):
    questions = [{
        'type': 'input',
        'name': 'driveId',
        'message': 'If you want to upload the directory to a specific Drive, insert the Drive id, else leave empty.'
    }]
else:

    with open("savedDrives.txt") as usedDrives:
        listOfUsedDrives = usedDrives.readlines()
        usedDrives.close()

    listOfUsedDrives = [x.strip() for x in listOfUsedDrives]

    questions = [
        {
            'type': 'confirm',
            'name': 'useOldDrive',
            'message': 'Do you want to use an already used Drive?'
        },
        {
            'type': 'list',
            'name': 'driveId',
            'message': 'In which Drive do you want to upload?',
            'when': lambda answers: answers['useOldDrive'],
            'choices': listOfUsedDrives
        },
        {
            'type': 'input',
            'name': 'driveId',
            'message': 'Insert the Drive id or leave empty.',
            'when': dontUseOldDrive
        }
    ]

if not os.path.isfile('savedPaths.txt'):
    questions.append({
        'type': 'input',
        'name': 'pathToUpload',
        'message': 'Which directory do you want to upload? (paste the absolute path)'
    })
else:

    with open("savedPaths.txt") as usedPath:
        listOfUsedPath = usedPath.readlines()
        usedPath.close()

    listOfUsedPath = [x.strip() for x in listOfUsedPath]

    questions.append({
        'type': 'confirm',
        'name': 'useOldPath',
        'message': 'Do you want to use an already used path?'
    })

    questions.append({
        'type': 'list',
        'name': 'pathToUpload',
        'message': 'In which directory do you want to upload?',
        'when': lambda answers: answers['useOldPath'],
        'choices': listOfUsedPath
    })

    questions.append({
        'type': 'input',
        'name': 'pathToUpload',
        'message': 'Which directory do you want to upload? (paste the absolute path)',
        'when': dontUseOldPath
    })

answers1 = prompt(questions, style=custom_style_3)

rootFolder = "root"
if answers1['driveId'] != "":
    rootFolder = answers1['driveId']

folderList = getFolderList("", answers1['driveId'])
directories = list(map(lambda x: x["title"], folderList))
directories.insert(0, rootFolder)

directoriesId = list(map(lambda x: x["id"], folderList))
directoriesId.insert(0, rootFolder)

questions = [{
    'type': 'list',
    'name': 'drivePosition',
    'message': 'Where you want to upload',
    'choices': directories
}]

answers2 = prompt(questions, style=custom_style_3)

if answers1['pathToUpload'] and answers1['pathToUpload'] != "":

    listOfUsedPath = []
    if os.path.isfile('savedPaths.txt'):
        with open("savedPaths.txt") as usedPath:
            listOfUsedPath = usedPath.readlines()
            usedPath.close()

    if answers1['pathToUpload'] + "\n" not in listOfUsedPath:
        savedOldPaths = open("savedPaths.txt", "a")
        savedOldPaths.write(answers1['pathToUpload'] + "\n")
        savedOldPaths.close()

if answers1['driveId'] and answers1['driveId'] != "":

    listOfUsedDrives = []
    if os.path.isfile('savedDrives.txt'):
        with open("savedDrives.txt") as usedDrives:
            listOfUsedDrives = usedDrives.readlines()
            usedDrives.close()

    if answers1['driveId'] + "\n" not in listOfUsedDrives:
        savedOldDrives = open("savedDrives.txt", "a")
        savedOldDrives.write(answers1['driveId'] + "\n")
        savedOldDrives.close()

indexDir = directories.index(answers2['drivePosition'])
folderId = directoriesId[indexDir]


# Funzione ricorsiva principale, crea le cartelle, e fa l'upload dei file
def fileUploader(fullPath, driveId, initialFolderId=""):
    pathName = os.path.basename(os.path.normpath(fullPath))

    itemsInFolderList = os.listdir(fullPath)

    for item in itemsInFolderList:

        if item[0] == "." or item == "desktop.ini" or item == ".DS_Store":
            print(item)
            continue

        idFolder = checkFolderExist(pathName, initialFolderId, driveId)

        if os.path.isdir(fullPath + PATH_SEPARATOR + item) and os.access(fullPath + PATH_SEPARATOR + item,
                                                                         os.X_OK | os.W_OK | os.R_OK):
            fileUploader(fullPath + PATH_SEPARATOR + item, driveId, idFolder)

        else:

            print(fullPath + PATH_SEPARATOR + item)

            uploadFileInsideFolder(item, idFolder, fullPath, driveId)


if __name__ == "__main__":
    fileUploader(answers1['pathToUpload'], answers1['driveId'], folderId)
