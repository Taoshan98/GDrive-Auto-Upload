import os
import platform
import datetime
from datetime import datetime

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gAuth = GoogleAuth()
gAuth.LocalWebserverAuth()
drive = GoogleDrive(gAuth)


def switch_demo(argument):
    switcher = {
        "Darwin": "/",
        "Linux": "/",
        "Windows": "\\",
    }

    return switcher.get(argument, "Invalid Platform")


PATH_SEPARATOR = switch_demo(platform.system())


# Crea Cartella verificando se è una root oppure una subdir
def createFolder(folderName, parentFolderId):
    folder = drive.CreateFile({'title': folderName, 'mimeType': "application/vnd.google-apps.folder"})

    if parentFolderId != "":
        folder = drive.CreateFile({'title': folderName, 'mimeType': "application/vnd.google-apps.folder",
                                   "parents": [{"id": parentFolderId}]})

    folder.Upload()

    return folder['id']


# Restituisce tutte le cartelle di default per la root del drive,
# il parametro folderId può specificare dove prendere l'elenco
def getFolderList(folderId, driveId):
    if driveId != "":

        if folderId == "":
            folderId = driveId

        return drive.ListFile(
            {
                'q': "'" + folderId + "' in parents "
                                      "and mimeType='application/vnd.google-apps.folder' "
                                      "and trashed=false",
                'corpora': 'teamDrive',
                'teamDriveId': driveId,
                'includeTeamDriveItems': True,
                'supportsTeamDrives': True
            }
        ).GetList()

    if folderId == "":
        folderId = "root"

    return drive.ListFile(
        {'q': "'" + folderId + "' in parents "
                               "and mimeType='application/vnd.google-apps.folder' "
                               "and trashed=false"
         }
    ).GetList()


foldersInFolderList = {}


# Verifica se una cartella esiste, eventualmente la crea
def checkFolderExist(folderName, parentFolderId="", driveId=""):
    global foldersInFolderList

    if folderName not in foldersInFolderList:
        listOfFolders = getFolderList(parentFolderId, driveId)
        foldersInFolderList[driveId if parentFolderId == "" else parentFolderId] = listOfFolders
    else:
        listOfFolders = foldersInFolderList.get(parentFolderId)

    folderNamesList = [title.get('title') for title in listOfFolders]

    currentFolder = ""

    if folderName in folderNamesList:
        currentFolder = folderNamesList.index(folderName)

    if currentFolder != "":
        return listOfFolders[currentFolder]['id']

    return createFolder(folderName, parentFolderId)


def uploadFile(fileName, fullPath, folderId):
    file = drive.CreateFile({'title': fileName, "parents": [{"kind": "drive#fileLink", "id": folderId}]})
    file.SetContentFile(fullPath + PATH_SEPARATOR + fileName)

    try:
        file.Upload()
    except ValueError:
        print("Error During Upload File: " + fullPath + PATH_SEPARATOR + fileName)


foldersContentList = {}


# Upload del file nella cartella di destinazione
def uploadFileInsideFolder(fileName, folderId, fullPath, driveId=""):
    global foldersContentList

    if folderId not in foldersContentList:

        if driveId != "":

            listOfFiles = drive.ListFile(
                {
                    'q': "'" + folderId + "' in parents and trashed=false",
                    'corpora': 'teamDrive',
                    'teamDriveId': driveId,
                    'includeTeamDriveItems': True,
                    'supportsTeamDrives': True
                }
            ).GetList()

        else:
            listOfFiles = drive.ListFile({'q': "'" + folderId + "' in parents and trashed=false"}).GetList()

        foldersContentList[folderId] = listOfFiles

    else:
        listOfFiles = foldersContentList.get(folderId)

    files = [title.get('title') for title in listOfFiles]

    if fileName not in files:
        uploadFile(fileName, fullPath, folderId)
        return True

    else:

        keyFileInList = files.index(fileName)

        tsOnDrive = datetime.timestamp(
            datetime.strptime(listOfFiles[keyFileInList]['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        tsOfFile = os.path.getmtime(fullPath + PATH_SEPARATOR + fileName)

        if tsOfFile > tsOnDrive:
            uploadFile(fileName, fullPath, folderId)
            return True

    return False
