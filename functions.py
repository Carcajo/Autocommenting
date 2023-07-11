from typing import Optional
from loguru import logger
from constants import *

import openai
import pandas as pd
import pygsheets

@logger.catch
def ask(prompt, context=''):
    openai.api_key = API_KEY
    model_id = 'gpt-3.5-turbo'
    conversation = []
    if len(context) > 0:
        conversation.append({'role': 'system', 'content': context})
    conversation.append({'role': 'user', 'content': prompt})

    max_retries = 3
    retry_delay = 25
    for retry in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=model_id,
                messages=conversation
            )
            api_usage = response['usage']
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error occurred: {e}")
            if retry < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Moving on.")
                break


@logger.catch
def status_check(channel_id: int):
    gc = pygsheets.authorize(service_file=SERVICE_FILE)
    doc = gc.open_by_url(URL)
    sheet = doc.open(SHEET_NAME)
    channel_status_cell = sheet.find(f'{channel_id}')
    df = sheet.get_as_df(start='A1')
    df_new = df.copy()
    row_index = df_new.index[df_new['channel_id'] == channel_id]
    df_new.Status[df_new.index == row_index[0]] = 'Ban'
    sheet.set_dataframe(df_new, start='A1', copy_head=True)


@logger.catch
def get_channel_data(service_file:str, table_url:str, list_name:str) -> pd.DataFrame:
    gc = pygsheets.authorize(service_file= service_file)
    doc = gc.open_by_url(table_url)
    sheet = doc.worksheet_by_title(list_name)
    return sheet.get_as_df(start='A1')


@logger.catch
def write_data(name, chanel_id, post, errors, filter=None, answer=None):
    gc = pygsheets.authorize(service_file=SERVICE_FILE)
    doc = gc.open_by_url(URL)
    sheet = doc.worksheet_by_title(SHEET_NAME_DATA)
    existing_data = sheet.get_as_df(start='A1')
    new_row = pd.DataFrame({'Name': [name], 'Channel_id': [chanel_id], 'Post': [post], 'Filter': [filter], 'Answer': [answer], 'Errors': [errors]})
    updated_data = pd.concat([existing_data, new_row], ignore_index=True)
    sheet.set_dataframe(updated_data, start='A1', copy_head=True)
