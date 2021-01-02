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
        savedOldPaths = open("savedPaths.txt", "a").write(answers1['pathToUpload'] + "\n")

if answers1['driveId'] and answers1['driveId'] != "":

    listOfUsedDrives = []
    if os.path.isfile('savedDrives.txt'):
        with open("savedDrives.txt") as usedDrives:
            listOfUsedDrives = usedDrives.readlines()
            usedDrives.close()

    if answers1['driveId'] + "\n" not in listOfUsedDrives:
        savedOldDrives = open("savedDrives.txt", "a").write(answers1['driveId'] + "\n")

indexDir = directories.index(answers2['drivePosition'])
folderId = directoriesId[indexDir]


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\n"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# Funzione ricorsiva principale, crea le cartelle, e fa l'upload dei file
def fileUploader(fullPath, driveId, initialFolderId="", i=1):
    pathName = os.path.basename(os.path.normpath(fullPath))

    itemsInFolderList = os.listdir(fullPath)
    listLen = len(itemsInFolderList)

    if initialFolderId == "":
        printProgressBar(0, listLen, prefix='Progress:', suffix='Complete', length=50)
    else:
        i = i

    for item in itemsInFolderList:

        folderId = checkFolderExist(pathName, initialFolderId, driveId)

        if os.path.isdir(fullPath + PATH_SEPARATOR + item) and os.access(fullPath + PATH_SEPARATOR + item,
                                                                         os.X_OK | os.W_OK | os.R_OK):
            i = fileUploader(fullPath + PATH_SEPARATOR + item, driveId, folderId, i)

        else:
            # Update Progress Bar
            time.sleep(0.1)
            printProgressBar(i, listLen, prefix='Uploading ' + item + ' Progress:', suffix='Complete', length=50)

            uploadFileInsideFolder(item, folderId, fullPath, driveId)

        i += 1

    return i


if __name__ == "__main__":
    fileUploader(answers1['pathToUpload'], answers1['driveId'], folderId)

# 0AB_CrG3NhQk-Uk9PVA
