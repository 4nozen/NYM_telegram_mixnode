import os
import json
import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher, types, html
from aiogram.enums import ParseMode, ChatAction
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.command import Command

from config import TG_TOKEN
from messages import TextMessage
from system_comm import validate_comma, add_mixnode, del_mixnode
from system_comm import new_user, get_mixnode_info
from classes import MixNode


logger.add("logs/{time:YYYY-MM-DD}.log", rotation="1 day")
bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def kb_mixnode_list(user_id) -> types.ReplyKeyboardMarkup:
    user_id = str(user_id.id)
    global builder_mixnodes_list
    try:
        with open(f"users/{str(user_id)}.json", "r") as file:
            data_from_json = json.load(file)
    except FileNotFoundError:
        new_user(user_id)
        pass
    builder_mixnodes_list = ReplyKeyboardBuilder()
    if len(data_from_json['mixnodes']) > 0:
        for key in data_from_json["mixnodes"]:
            builder_mixnodes_list.add(types.KeyboardButton(text='№: '+str(key['info']['mix_id'])))
    else:
        logger.warning(f"{user_id}: No mixnodes")
    builder_mixnodes_list.adjust(4)


@dp.message(Command("start"))
# @dp.message(Command("restart"))
async def cmd_start(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    new_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
    logger.debug(f"{message.from_user.id}: /start|restart")
    kb_mixnode_list(message.from_user)
    await message.bot.send_message(message.chat.id, TextMessage.HELP, reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True))


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    logger.debug(f"{message.from_user.id}: /help")
    kb_mixnode_list(message.from_user)
    await message.bot.send_message(message.chat.id, TextMessage.HELP, reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True))


@dp.message(Command("add"))
async def cmd_add(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    comma = validate_comma(message)
    if comma is True:
        user_id = message.from_user.id
        node_id = message.text.split()[1]
        if add_mixnode(user_id, node_id) is True:
            kb_mixnode_list(message.from_user)
            await message.bot.send_message(message.chat.id, f"node added: {node_id}", reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True))
            logger.debug(f"{message.from_user.id} add node_id: {node_id}")
        else:
            kb_mixnode_list(message.from_user)
            await message.bot.send_message(message.chat.id, f"node not added: {node_id}")
            logger.debug(f"{message.from_user.id} not add node_id: {node_id}")
    else:
        logger.debug(f"{message.from_user.id} add error: {comma}")
        kb_mixnode_list(message.from_user)
        await message.bot.send_message(message.chat.id, comma, reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True))


@dp.message(Command("del"))
async def cmd_del(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    comma = validate_comma(message)
    if comma is True:
        user_id = message.from_user.id
        node_id = message.text.split()[1]
        with open(f"users/{user_id}.json", "r") as file:
            data_from_json = json.load(file)
        for key in data_from_json["mixnodes"]:
            if key['info']['mix_id'] == int(node_id):
                del_mixnode(user_id, node_id)
            else:
                pass
        logger.debug(f"{message.from_user.id} del node_id: {node_id}")
        kb_mixnode_list(message.from_user)
        await message.bot.send_message(message.chat.id, f"node deleted: {node_id}", reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True))
    else:
        logger.debug(f"{message.from_user.id} del error: {comma}")
        kb_mixnode_list(message.from_user)
        await message.bot.send_message(message.chat.id, comma, reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True))


@dp.message()
async def cmd_echo(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    if message.text.split()[0] == '№:' and message.text.split()[1].isdigit():
        node_id = message.text.split()[1]
        kb_mixnode_list(message.from_user)
        await message.bot.send_message(
            message.chat.id,
            get_mixnode_info(str(message.from_user.id),
            str(node_id)),
            reply_markup=builder_mixnodes_list.as_markup(resize_keyboard=True)
            )
    logger.info(f"{message.from_user.id}: {message.text}")


def find_different_elements(list_old, list_new):
    out = dict()
    list_old = set(list_old)
    list_new = set(list_new)
    only_in_list1 = list(list_old - list_new)
    only_in_list2 = list(list_new - list_old)
    if only_in_list1 != []:
        out = {'added':only_in_list1}
        return out
    elif only_in_list2 != []:
        out = {'removed':only_in_list2}
        return out
    else:
        return 'nothing changed'


async def send_message_to_user(user_id: int, text: str):
    try:
        await bot.send_message(user_id, text)
        print(f"Сообщение отправлено пользователю {user_id}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


async def info_fetcher():
    while True:
        for file in os.listdir("users/"):
            if file.endswith(".json"):
                file_path = os.path.join("users", file)
                with open(file_path, "r") as file:
                    data_from_json = json.load(file)
                    mix_list = []
                    for key in data_from_json["mixnodes"]:
                        delegations_old = sorted([i['owner'] for i in key["delegations"]])
                        mix_node = MixNode(str(key['info']['mix_id']))
                        mixnode_delegations = mix_node.get_mixnode_delegations()
                        mix_list.append({
                            'info':mix_node.get_mixnode_info(),
                            'delegations':mixnode_delegations,
                            'stats':mix_node.get_mixnode_stats(),
                        })
                        delegations_new = sorted([i["owner"] for i in mixnode_delegations])
                        different_elements = find_different_elements(delegations_old, delegations_new)
                        if different_elements != 'nothing changed':
                            if different_elements.keys() == {'added'}:
                                await send_message_to_user(
                                    file_path.split("/")[1].split(".")[0],
                                    # f'INFO:mixnode {key["info"]["mix_id"]} delegator added {different_elements["added"]}'
                                    f'\n\
INFO: {html.italic("mixnode №")} {html.bold(key["info"]["mix_id"])}\n\
delegator:\n\
{", ".join(different_elements["added"])}\n\
{html.bold("ADDED")}\n\
                                    ')
                                continue
                            if different_elements.keys() == {'removed'}:
                                await send_message_to_user(
                                    file_path.split("/")[1].split(".")[0],
                                    f'\n\
INFO: {html.italic("mixnode №")} {html.bold(key["info"]["mix_id"])}\n\
delegator:\n\
{", ".join(different_elements["removed"])}\n\
{html.bold("REMOVED")}\n\
                                    ')
                                continue
                    data_from_json["mixnodes"] = mix_list
                try:
                    with open(f"{file_path}", "w") as file:
                        json.dump(data_from_json, file, indent=4, ensure_ascii=False)
                    print(f"OK writing {file_path}")
                except Exception:
                    print(f"Error while writing file {file_path}")
        await asyncio.sleep(300)


async def main_run():
    if not os.path.exists("users"):
        os.mkdir("users")
    logger.warning("Starting bot")
    asyncio.create_task(info_fetcher())
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main_run())
        # asyncio.run(main_run(), debug=True)
    except KeyboardInterrupt:
        print(KeyboardInterrupt)
    logger.warning("Closing. Bye-bye!")
