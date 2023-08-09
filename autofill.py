import requests
import json
from format import format
from parser import parse
import gspread
from constants import *
from oauth2client.service_account import ServiceAccountCredentials


channels = format(parse('https://tlgrm.ru/channels/business', 1))
print(channels)

bot_token = BOT_TOKEN

def main():
    print('start')
    for url_tg in channels:
        chat_name = url_tg.split("/")[-1]
        url = f"https://api.telegram.org/bot{bot_token}/getChat?chat_id=@{chat_name}"

        response = requests.get(url)
        json_data = response.json()

        json_string = json.dumps(json_data, indent=4)
        start_substring_chat = '"id": '
        start_index_chat = json_string.find(start_substring_chat)

        start_substring_channel = '"linked_chat_id": '
        start_index_channel = json_string.find(start_substring_channel)

        desired_substring_chat = json_string[start_index_chat + len(start_substring_chat): start_index_chat + len(start_substring_chat) + 14]

        desired_substring_channel = json_string[start_index_channel + len(start_substring_channel): start_index_channel + len(start_substring_channel) + 14]

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_JSON, scope)

        # Авторизуемся и открываем таблицу
        gc = gspread.authorize(credentials)
        spreadsheet_key = SPREADSHEET_KEY
        worksheet_name = WORKSHEET_NAME
        worksheet = gc.open_by_key(spreadsheet_key).worksheet(worksheet_name)

        column_names = ['Link', 'Channel_id', 'Chat_id', 'Status']
        if desired_substring_channel == '"result":':
            continue

        header = worksheet.row_values(1)
        column_indexes = [header.index(column_name) + 1 for column_name in column_names]

        values_to_write = [url_tg, desired_substring_chat, desired_substring_channel, "Open"]

        last_row = len(worksheet.col_values(1)) + 1

        for index, value in zip(column_indexes, values_to_write):
            worksheet.update_cell(last_row, index, value)

main()
