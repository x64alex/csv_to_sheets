from googleapiclient.discovery import build 
from google.oauth2 import service_account

import webbrowser
import pandas as pd
import os
import sys
import json

SCOPES = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]
def get_credentials_path():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_directory, 'credentials.json')


def create(title, credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)

    spreadsheet_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    spreadsheet_details = {
    'properties': {
        'title': title
        }
    }
    sheet = spreadsheet_service.spreadsheets().create(body=spreadsheet_details,
                                    fields='spreadsheetId').execute()
    sheet_id = sheet.get('spreadsheetId')
    permission = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'alexcantor64@gmail.com'
    }
    drive_service.permissions().create(fileId=sheet_id, body=permission).execute()

    return sheet_id, spreadsheet_service

def drop_extension(file_name):
    return os.path.splitext(file_name)[0]

def drop_path(full_path):
    return os.path.basename(full_path)    

def get_file_name_from_path(file_name):
    file = drop_path(file_name)
    file_name = drop_extension(file)
    return file_name


def open_sheet(sheet_id):
    spreadsheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}'
    webbrowser.open(spreadsheet_url)

def read_csv(csv_file):
    df = pd.read_csv(csv_file, header=None)
    data = df.values.tolist()
    num_rows, num_columns = df.shape
    
    return data, num_rows, num_columns

def write(path, credentials_path):
    spreadsheet_id, spreadsheet_service = create(get_file_name_from_path(path), credentials_path)
    print('Spreadsheet created with ID: {0}'.format(spreadsheet_id))
    values, num_rows, num_columns = read_csv(path)
    range_name = f'Sheet1!A1:{chr(ord("A") + num_columns - 1)}{num_rows}'

    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    result = spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

    open_sheet(spreadsheet_id)

def update_json(file_path, new_json_string):
    try:
        new_data = json.loads(new_json_string)

        with open(file_path, 'w') as json_file:
            json.dump(new_data, json_file, indent=2)

        print("JSON file updated successfully.")
    except ValueError as e:
        print(f"Error: Invalid JSON string provided. {e}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  For writing to Google Sheets: python -write sheets.py /path/to/csv_file")
        print("  For updating JSON: python sheets.py -update '{\"key\":\"value\"}'")
        sys.exit(1)

    mode = sys.argv[1]
    credentials_path = get_credentials_path()

    if mode == "-writeJson":
        if len(sys.argv) != 4:
            print("Bad")

        file_path = sys.argv[2]
        json_path = sys.argv[3]
        write(file_path, json_path)
    elif mode == "-update":
        json_string = sys.argv[2]
        print(json_string)
        update_json(credentials_path, json_string)
    elif mode == "-write":
        file_path = sys.argv[2]
        write(file_path, credentials_path)
    else:
        print("Bad command")