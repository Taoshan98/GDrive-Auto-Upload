import os
import platform

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gAuth = GoogleAuth()
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


# Verifica se una cartella esiste, eventualmente la crea
def checkFolderExist(folderName, parentFolderId="", driveId=""):
    listOfFolders = getFolderList(parentFolderId, driveId)

    folderNames = list(map(lambda x: x["title"], listOfFolders))

    currentFolder = ""

    try:
        currentFolder = folderNames.index(folderName)
    except ValueError:
        pass

    if currentFolder != "":
        return listOfFolders[currentFolder]['id']

    return createFolder(folderName, parentFolderId)


# Upload del file nella cartella di destinazione
def uploadFileInsideFolder(fileName, folderId, fullPath, driveId=""):
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

    files = list(map(lambda x: x["title"], listOfFiles))

    if fileName not in files:

        if fileName != "desktop.ini" or fileName != ".DS_Store":
            file = drive.CreateFile({'title': fileName, "parents": [{"kind": "drive#fileLink", "id": folderId}]})
            file.SetContentFile(fullPath + PATH_SEPARATOR + fileName)

            file.Upload()
            return True

    return False
