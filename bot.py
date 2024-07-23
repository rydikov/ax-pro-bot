
import os
import socket
import asyncio
import logging
import sys


from aiogram.client.bot import DefaultBotProperties
from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hcode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from axpro import AxPro
from axpro.axpro import UnexpectedResponseCodeError


ALREADY_ARMED_STATUS_CODE = 1073774603

TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_ADMIN_IDS = os.environ.get('TELEGRAM_ADMIN_IDS').split(',')

axpro = AxPro(
    os.environ.get('AX_PRO_HOST'), 
    os.environ.get('AX_PRO_USER'), 
    os.environ.get('AX_PRO_PASSWORD')
)

dp = Dispatcher()
admin_ids = [int(admin_id) for admin_id in TELEGRAM_ADMIN_IDS]

dp.message.filter(F.from_user.id.in_(admin_ids))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

###

@dp.message(Command('arm'))
async def command_arm_away(message: Message) -> None:
    resp = axpro.arm_away()
    if resp['errorCode'] == 1073774603:
        axpro.disarm()
        resp = axpro.arm_away()
    answer = 'OK' if resp['statusCode'] == 1 else resp['errorMsg']
    await message.answer(answer)


@dp.message(Command('disarm'))
async def command_disarm(message: Message) -> None:
    resp = axpro.disarm()
    answer = 'OK' if resp['statusCode'] == 1 else resp['errorMsg']
    await message.answer(answer)


@dp.message(Command('status'))
async def command_status(message: Message) -> None:
    answer = ""
    resp = axpro.subsystem_status()
    for area in resp['SubSysList']:
        if area['SubSys']['enabled']:
            status = {
                'disarm': 'Снято с охраны', 
                'arm': 'Поставлено на охрану в ночном режиме',
                'away': 'Поставлено на охрану при отсутствии людей'
            }[area['SubSys']['arming']]
            answer += f"{area['SubSys']['name']}: {status} \n"
    await message.answer(answer)


@dp.message(Command('temperature'))
async def command_temperature(message: Message) -> None:
    answer = ""

    resp = axpro.zone_status()
    for zone in resp['ZoneList']:
        answer += f"{zone['Zone']['name']}: {zone['Zone']['temperature']} \n"

    resp = axpro.siren_status()
    for siren in resp['SirenList']:
        answer += f"{siren['Siren']['name']}: {siren['Siren']['temperature']} \n"

    await message.answer(answer)


@dp.message(Command('beep'))
async def command_beep(message: Message) -> None:
    resp = axpro.siren_test(1)
    await message.answer(resp['statusString'])

###

@dp.message()
async def default_handler(message: types.Message) -> None:
    await message.answer("Unknown command")


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
