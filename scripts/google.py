from __future__ import print_function
import pickle
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import httplib2
import os
import io
import argparse
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    """Shows basic usage of the Google Drive API.
    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

# Create_Service is used to create the google drive api server instance
def Create_Service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def upload_files():
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Create the google drive api server instance
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # Folder Id is found by clicking on the folder you want the file to be uploaded to and copy and pasting the last part of the url
    folder_id = '1pM71zkH5K67nQb-fG5MSdWcegdO97u-u'
    file_name = ['testimage.jpg']
    # Use https://learndataanalysis.org/commonly-used-mime-types/ to find the correct mimetype for your folder type
    mime_type = ['image/jpeg']

    # iterates each element within the file list by zipping the contnets inside the file_name and mime_type together
    for file_name, mime_type in zip(file_name, mime_type):
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]

        }

        media = MediaFileUpload('/Users/artimbanyte/cornucopia/test/test_files/{0}'.format(file_name),
                                mimetype=mime_type)
        # Upload the files by uisng the service function
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()


upload_files()


def download_files():
    # file_id is found on gogole drive by opening the wanted file in a new window and copy and pasting the last part of the URL
    file_id = ['1xPcUK1EIBTYQPJQOHJFwB2ciX1VJXUYn']
    file_name = ['test.jpg']
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    # Create the google drive api server instance
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # Iterates the each element within the file list by zipping the contents within file_id and file_name together
    for file_id, file_name in zip(file_id, file_name):
        request = service.files().get_media(fileId=file_id)

        #stores the output from the BytesIO module as fh
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)

        # set the deafult track of the download as false
        done = False

        while not done:
            status, done = downloader.next_chunk()
            print('Download progress {0}'.format(status.progress() * 100))

        # seeks if the download progress is at 0%
        fh.seek(0)

        with open(os.path.join('/Users/artimbanyte/cornucopia/test/test_files/', file_name), 'wb') as f:
            f.write(fh.read())
            f.close()


download_files()


if __name__ == '__main__':
    main()