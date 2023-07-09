# -*- coding: utf-8 -*-
import asyncio

from pyrogram import Client, filters
from datetime import datetime
from random import randint
from typing import Optional
from loguru import logger
from private_data import *
from constants import *
from promts import *
from functions import *


logger.add('Max\'s_bot_log_{time}.log', format='{level} {time} {message}', rotation='10:00', compression='zip')


@logger.catch
def main():
    chats = {}
    channels = []

    df = get_channel_data(
        service_file=SERVICE_FILE,
        table_url=URL,
        list_name=SHEET_NAME
    )
    for index, row in df.iterrows():
        channels.append(row['Channel_id'])
        chats[row['Channel_id']] = row['Chat_id']
        print(f"Link: {row['Link']}, Channel: {row['Channel_id']}, Chat: {row['Chat_id']}")

    @app.on_message(filters.chat(channels))
    async def handle_message(client, message):
        try:
            txt = ''
            if message.text != None:
                txt = message.text
            elif message.caption != None:
                txt = message.caption
            chat_nm = message.chat.title
            channel_id = message.chat.id
            chat_id = chats[channel_id]
            history = app.get_chat_history(chat_id, limit=100)
            await asyncio.sleep(5)

            async for msg in history:
                time = randint(10, 20)
                if msg.forward_from_message_id == message.id:
                    if txt != '' and len(txt) > 10:
                        try:
                            check = ask(prepare_filter, context=txt)
                        except Exception as e:
                            logger.error(f'{e}\n Лимит запросов в минуту в СhatGPT')
                            check = 'False'
                        await asyncio.sleep(5)
                        logger.debug(f'{check}')

                        if check == 'True':
                            logger.info('Start writing message!')
                            try:
                                response = ask(prepare,context=txt)
                                msg_id = msg.id
                                logger.info(f'\nNew message!\nChannel name:{chat_nm}\nMESSAGE ID:{msg_id}' \
                                f'\nChannel id: {channel_id}\nMessage: {txt}')
                                logger.info(f'Send message in {time} sec.')
                                await asyncio.sleep(time)
                                responsed = await app.send_message(
                                chat_id,
                                response,
                                reply_to_message_id=msg_id)
                                write_data(chat_nm, channel_id, txt, errors='Нет ошибок2', filter=check, answer=response)
                                break

                            except Exception as e:
                                logger.error(f'{e}')
                                response = 'Прикольно)'
                                responsed = await app.send_message(
                                chat_id,
                                response,
                                reply_to_message_id=msg_id)

                            logger.info(f'{datetime.now()}\nDONE!\nChannel name:{chat_nm}\nMESSAGE ID:{msg_id}' \
                                f'\nChannel id: {channel_id}\nMessage text:{txt}\n')
                            logger.info(f'\nMax Reply:\n {response}\n')
                            try:
                                await client.send_reaction(chat_id, responsed.id, "🔥")
                            except:
                                await client.send_reaction(chat_id, responsed.id, "👍")
                        else:
                            if check:
                                write_data(chat_nm, channel_id, txt, errors='Нет ошибок', filter=check, answer='Нет ответа')
                            else:
                                write_data(chat_nm, channel_id, txt, errors='Нет ошибок', filter="Проверка не прошла", answer='Нет ответа')
                            logger.info(f"Message is not target theme, text: {txt}")
                    else:
                        logger.info('Message don\'t have text or len < 10')
                        break

        except Exception as e:
                await client.send_message(
                        chat_id=debug_chat_id,
                        text=f"Chat name:{chat_nm}\n Chat id:{chat_id}\n" \
                        f"Max Error:\n{e}")
                write_data(chat_nm, channel_id, txt, e, check, response='Нет ответа1')
                e = str(e)
                if '404' or 'CHANNEL_PRIVATE' in e:
                    status_check(int(channel_id))
                pass


if __name__ == '__main__':
    logger.info('Started!')

    app = Client(
        'New',
        api_id,
        api_hash
        )

    main()
    app.run()
