import asyncio
from json import load, dump
from time import time
from math import sqrt

import httpx
from highrise import BaseBot, User, Position, AnchorPosition, Reaction
from highrise.__main__ import *
from highrise import BaseBot, User
from random import randrange
from words_filter import ProfanityChecker
from collections import defaultdict
from datetime import datetime, timedelta
import aiohttp


class ModeratorBot(BaseBot):

    checker = ProfanityChecker()

    banned_users = None
    filter_words = None
    ignorewords = None
    defaultfilter = None
    warnlimit = None
    warnmode = None
    set_welcome = None
    welcome = None
    warntime = None
    mute_duration = None

    api_key = '7bfb8522233ce607a7cae399c640e9867d4f4351bae7553b66490838a348659e'
    identifier: str = "/m "
    warnings = defaultdict(lambda: {'count': 0, 'last_warning_time': None})
    users: dict = {}

    COMMAND_INSTRUCTIONS: list[str] = [
        "help - list all commands",
        "welcome <on/off> - Активировать/Отключить приветствие",
        "setwelcome <message> - Установить приветствие",
        "ban <username> <time> - Забанить пользователя",
        "unban <username> - Разбанить пользователя",
        "mute <username> <lenght> - Замутить пользователя",
        "unmute <username> - Размутить пользователя",
        "kick <username> - Выгнать пользователя",
        "warn <username> - Дать предупреждение",
        "warns - Список предупреждений",
        "resetwarn <username> - Сбросить предупреждения пользователя до 0",
        "resetallwarn - Сбросить предупреждения всех пользователей",
        "wanrmode <ban/kick/mute> - Функция, которая сработает после пересечения лимита предупреждений ban/kick/mute",
        "warnlimit <integer> - Лимит предупреждений",
        "warntime <time> - Время жизни предупреждений",
        "defaultfilter <on/off> - Включение/Выключение базовой фильтрации",
        "filters - Список фильтров",
        "filter <trigger> - Добавить фильтер",
        "ignore <word> - Слово, которое будет игнорировать фильтрацию"
        "flood <on/off> - Функция спама включить/выключить",
        "floodtimer <time> - Промежуток времени, чтобы сообщения считались флудом",
        "floodmode <ban/kick/mute> - Функция, которая будет использована, если пользователь флудит"
    ]

    MODE_INSTANCES = ["mute", "kick", "ban"]
    CHOICES = ["on", "off"]
    USER_WELCOME_MESSAGE: str = "\nДобро пожаловать в нашу комнату. \n\n📜 Правила: /rules \n🤖 Помощь: /help"

    async def before_start(self, tg: TaskGroup) -> None:

        moderator_params = await self.get_moderator_params()

        self.welcome = moderator_params.get('welcome')
        self.set_welcome = moderator_params.get('set_welcome')

        self.mute_duration = moderator_params.get('mute_duration')

        self.warnmode = moderator_params.get('warnmode')
        self.warnlimit = moderator_params.get('warnlimit')
        self.warntime = moderator_params.get('warntime')

        self.defaultfilter = moderator_params.get('defaultfilter')
        self.ignorewords = moderator_params.get('ignorewords')
        self.filter_words = moderator_params.get('filter_words')
        self.banned_users = moderator_params.get('banned')

    async def on_user_join(self, user: User, *args, **kwargs) -> None:
        """On a user joining the room."""
        await self.create_new_user(user)

        user_warnings = self.warnings.get(user.id, None)

        if user_warnings is None:
            self.warnings[user.id] = {'count': 0, 'last_warning_time': None, 'username': user.username}

        if self.welcome is True:
            welcome_user = f'{self.set_welcome}'
            await self.whisper_to_user(user, welcome_user)

    async def on_user_leave(self, user: User) -> None:
        """On a user leaving the room."""
        pass

    async def on_chat(self, user: User, message: str) -> None:
        """On a received room-wide chat."""

        message = message.lower()
        response = await self.checker.check(message)
        if message.startswith(self.identifier):
            await self.handle_command(user, message.removeprefix(self.identifier))
        if response is True:
            user_warnings = self.warnings.get(user.id, {'count': 0})
            if user_warnings['count'] >= 3:
                await self.highrise.moderate_room(user.id, 'mute', 10000)
                await self.whisper_to_user(user, 'За неоднократное нарушение правил, вы получаете мут на 12 часов.')
            else:
                self.warnings[user.id]['username'] = user.username
                self.warnings[user.id]['count'] += 1
                self.warnings[user.id]['last_warning_time'] = datetime.now()

                await self.highrise.send_emote('emoji-angry')
                await self.whisper_to_user(user, f'Вы получаете предупреждение {self.warnings[user.id]["count"]}'
                                                 f'/{self.warnlimit}.'
                                                 f'\n\n{self.warnlimit} предупреждения мут {self.mute_duration} часов')

    async def on_reaction(self, user: User, reaction: Reaction, receiver: User) -> None:
        """Called when someone reacts in the room."""
        print(f"[REACTION ] {user.username} {reaction} {receiver.username}")

    async def handle_command(self, user: User, message: str) -> None:
        """Handler for all bot commands"""

        # Handle bot commands
        match message.split(maxsplit=1):
            case ['welcome', choice]:
                if choice == 'off' or choice == 'on':
                    await self.welcome_onoff(choice)
                    await self.whisper_to_user(user, f"Функция приветствия изменена")
                else:
                    await self.whisper_to_user(user, f"Выберите между /m welcome off или /m welcome on")

            case ['setwelcome', message]:
                await self.set_welcome_message(message)
                await self.whisper_to_user(user, f"Приветствие изменено")

            case ['ban', username_lenght]:
                try:
                    username, lenght = username_lenght.split()
                    await self.ban_user(username, int(lenght))
                except ValueError:
                    await self.whisper_to_user(user, f"Ошибка, пример /m ban username 10000")

            case ['unban', username]:
                try:
                    await self.unban_user(username)
                except ValueError:
                    await self.whisper_to_user(user, f"Ошибка, пример /m unmute username")

            case ['mute', username_lenght]:
                try:
                    username, lenght = username_lenght.split()
                    await self.mute_user(username, int(lenght))
                except ValueError:
                    await self.whisper_to_user(user, f"Ошибка, пример /m mute username 10000")

            case ['unmute', username]:
                try:
                    await self.unmute_user(username)
                except ValueError:
                    await self.whisper_to_user(user, f"Ошибка, пример /m unmute username")

            case ['kick', username]:
                try:
                    await self.kick_user(username)
                except ValueError:
                    await self.whisper_to_user(user, f"Ошибка, пример /m kick username")
            case ['warn', username_reason]:
                username, reason = username_reason.split(maxsplit=1)
                user_id = await self.get_user(username)

                self.warnings[user_id]['count'] += 1
                self.warnings[user_id]['last_warning_time'] = datetime.now()

                await self.highrise.send_whisper(user_id, f"Вы получаете предупреждение "
                                                          f"{self.warnings[user_id]['count']}/{self.warnlimit} "
                                                          f"\n\nПо причине: {reason}")
            case ['warns']:
                users_warnings = str()
                if self.warnings.values():
                    for data in self.warnings.values():
                        users_warnings += f"\nUsername: {data.get('username')} Count: {data.get('count')}"
                    await self.whisper_to_user(user, users_warnings)
                else:
                    await self.whisper_to_user(user, 'Нету активных предупреждений')
            case ['resetwarn', username]:
                user_id = await self.get_user(username)
                self.warnings[user_id]['count'] = 0
                await self.whisper_to_user(user, f"Предупреждения для {username} сброшены")
            case ['resetallwarn']:
                self.warnings = defaultdict(lambda: {'count': 0, 'last_warning_time': None})
                await self.whisper_to_user(user, f"Предупреждения сброшены")
            case ['warnmode', mode]:
                if mode in self.MODE_INSTANCES:
                    responce = await self.change_warnmode(mode)
                    if responce.status_code == 200:
                        await self.whisper_to_user(user, f"Warn mode успешно изменён на {mode}")
                    else:
                        await self.whisper_to_user(user, f"Ошибка при изменении")
                else:
                    await self.whisper_to_user(user, f"Выберите между <ban/kick/mute>")

            case ['warnlimit', warnlimit]:
                if warnlimit.isdigit():
                    response = await self.change_limit(int(warnlimit))
                    if response == 200:
                        await self.whisper_to_user(user, f"Warn limit успешно изменён на {warnlimit}")
                    else:
                        await self.whisper_to_user(user, f"Ошибка при изменении")
                else:
                    await self.whisper_to_user(user, f"Ошибка, пример /m warnlimit 10")
            case ['defaultfilter', choice]:
                if choice in self.CHOICES:
                    response = await self.change_defaultfilter(choice)
                    if response == 200:
                        await self.whisper_to_user(user, f"Default filter {choice}")
                    else:
                        await self.whisper_to_user(user, f"Ошибка при изменении")
                else:
                    await self.whisper_to_user(user, f"Ошибка, пример /m defaultfilter on")

            case ['filters']:
                await self.whisper_to_user(user, f"Filters: {self.filter_words}")
            case ['filter', trigger]:
                response = await self.add_filter(trigger)
                if response == 200:
                    await self.whisper_to_user(user, 'Фильтр успешно добавлен')
                else:
                    await self.whisper_to_user(user, 'Ошибка при добавлении фильтра')
            case ['dfilter', trigger]:
                response = await self.delete_filter(trigger)
                if response == 204 or response == 200:
                    await self.whisper_to_user(user, 'Фильтр успешно удалён')
                    await self.remove_word_from_string('filter_words', trigger)
                else:
                    await self.whisper_to_user(user, 'Ошибка при удалении фильтра')
            case ['ignorewords']:
                await self.whisper_to_user(user, f"Ingored Word: {self.ignorewords}")
            case ['ignore', trigger]:
                response = await self.add_ignore(trigger)
                if response == 200:
                    await self.whisper_to_user(user, 'Ignore успешно добавлен')
                else:
                    await self.whisper_to_user(user, 'Ошибка при добавлении ignore')
            case ['dignore', trigger]:
                response = await self.delete_filter(trigger)
                if response == 204 or response == 200:
                    await self.whisper_to_user(user, 'Игнор успешно удалён')
                    await self.remove_word_from_string('ignorewords', trigger)
                else:
                    await self.whisper_to_user(user, 'Ошибка при удалении игнора')
            case 'help':
                await self.whisper_to_user(user, "\n" + "\n".join(self.COMMAND_INSTRUCTIONS))

            case _:
                await self.whisper_to_user(user, f"Not a valid command. Use {self.identifier}help to see the list of commands")


    async def whisper_to_user(self, user: User, message: str) -> None:
        """Whispers a message to a user."""
        await self.highrise.send_whisper(user.id, message)

    async def check_and_warn_user(self, user_id):
        now = datetime.now()

        # Получаем предупреждения пользователя из словаря
        user_warnings = self.warnings.get(user_id, None)

        if user_warnings is None:
            self.warnings[user_id] = {'count': 0, 'last_warning_time': None}

        # Проверяем, прошло ли уже 24 часа с последнего предупреждения
        if user_warnings['last_warning_time'] is not None:
            time_since_last_warning = now - user_warnings['last_warning_time']
            if time_since_last_warning >= timedelta(hours=24):
                user_warnings['count'] = 0  # Сбрасываем количество предупреждений, если прошло больше 24 часов

        # Увеличиваем количество предупреждений пользователя
        user_warnings['count'] += 1
        user_warnings['last_warning_time'] = now

        # Проверяем, достиг ли пользователь трех предупреждений
        if user_warnings['count'] >= 3:
            # Применяем мут на час и сбрасываем количество предупреждений
            user_warnings['count'] = 0
            return True

    async def create_new_user(self, user: User) -> httpx.Response:
        """Retrieves and returns the weather data based on provided location"""
        async with httpx.AsyncClient() as client:
            data = {
                "username": user.username,
                "user_id": user.id
            }
            response = await client.post(f"http://127.0.0.1:8000/api/players/", data=data)
            return response

    async def get_moderator_params(self) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            data = {
                "api_key": self.api_key,
            }
            response = await client.post(f"http://127.0.0.1:8000/api/bots/", data=data)
            return response.json()

    async def welcome_onoff(self, welcome_choice: str) -> httpx.Response:
        """Retrieves and returns the weather data based on provided location"""
        async with httpx.AsyncClient() as client:
            if welcome_choice.lower() == "on":
                welcome_choice = True
            else:
                welcome_choice = False

            data = {
                "api_key": self.api_key,
                "welcome": welcome_choice
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)
            if response.status_code == 200:
                welcome = response.json().get("welcome")
                self.welcome = welcome

            return response

    async def set_welcome_message(self, message: str) -> httpx.Response:
        """Retrieves and returns the weather data based on provided location"""
        async with httpx.AsyncClient() as client:
            data = {
                "api_key": self.api_key,
                "set_welcome": message
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)

            if response.status_code == 200:
                set_welcome = response.json().get("set_welcome")
                self.set_welcome = set_welcome

            return response

    async def ban_user(self, username: str, lenght: int):
        """Retrieves and returns the weather data based on provided location"""
        user_id = await self.get_user(username)
        await self.highrise.moderate_room(user_id, 'ban', lenght)

    async def unban_user(self, username: str):
        """Retrieves and returns the weather data based on provided location"""
        user_id = await self.get_user(username)
        await self.highrise.moderate_room(user_id, 'unban')

    async def mute_user(self, username: str, lenght: int):
        """Retrieves and returns the weather data based on provided location"""
        user_id = await self.get_user(username)
        await self.highrise.moderate_room(user_id, 'mute', lenght)

    async def unmute_user(self, username: str):
        """Retrieves and returns the weather data based on provided location"""
        user_id = await self.get_user(username)
        await self.highrise.moderate_room(user_id, 'mute', 1)

    async def kick_user(self, username: str):
        """Retrieves and returns the weather data based on provided location"""
        user_id = await self.get_user(username)
        await self.highrise.moderate_room(user_id, 'kick', )

    async def change_warnmode(self, mode: str):
        async with httpx.AsyncClient() as client:
            data = {
                "api_key": self.api_key,
                "warnmode": mode
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)

            if response.status_code == 200:
                warnmode = response.json().get("warnmode")
                self.warnmode = warnmode

            return response

    async def change_limit(self, warnlimit: int):
        async with httpx.AsyncClient() as client:
            data = {
                "api_key": self.api_key,
                "warnlimit": warnlimit
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)

            if response.status_code == 200:
                warnlimit = response.json().get("warnlimit")
                self.warnlimit = warnlimit

            return response.status_code

    async def change_defaultfilter(self, choice: str):
        async with httpx.AsyncClient() as client:

            if choice == "on":
                defaultfilter = True
            else:
                defaultfilter = False

            data = {
                "api_key": self.api_key,
                "defaultfilter": defaultfilter
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)

            if response.status_code == 200:
                defaultfilter = response.json().get("defaultfilter")
                self.defaultfilter = defaultfilter

            return response.status_code

    async def add_filter(self, trigger: str):
        async with httpx.AsyncClient() as client:

            data = {
                "api_key": self.api_key,
                "filter_words": trigger,
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)

            if response.status_code == 200:
                filter_words = response.json().get("filter_words")
                self.filter_words = filter_words

            return response.status_code

    async def delete_filter(self, trigger: str):
        async with httpx.AsyncClient() as client:

            params = {
                "api_key": self.api_key,
                "word": trigger,
                "field": "filter_words"
            }

            response = await client.delete(f"http://127.0.0.1:8000/api/bots/", params=params)

            if response.status_code == 200:
                filter_words = response.json().get("filter_words")
                self.filter_words = filter_words

            return response.status_code

    async def add_ignore(self, trigger: str):
        async with httpx.AsyncClient() as client:

            data = {
                "api_key": self.api_key,
                "ignorewords": trigger,
            }

            response = await client.put(f"http://127.0.0.1:8000/api/bots/", data=data)

            if response.status_code == 200:
                ignorewords = response.json().get("ignorewords")
                self.ignorewords = ignorewords

            return response.status_code

    async def delete_ignore(self, trigger: str):
        async with httpx.AsyncClient() as client:

            params = {
                "api_key": self.api_key,
                "word": trigger,
                "field": "ignorewords"
            }

            response = await client.delete(f"http://127.0.0.1:8000/api/bots/", params=params)

            if response.status_code == 200:
                filter_words = response.json().get("ignorewords")
                self.filter_words = filter_words

            return response.status_code

    async def get_user(self, username):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://webapi.highrise.game/users?username={username}",)
            if response.status_code == 200:
                try:
                    user_id = response.json().get('users')[0].get('user_id')
                except IndexError:
                    user_id = None
            return user_id

    async def remove_word_from_string(self, field_name, word_to_remove):
        if field_name == 'ignorewords':
            words = self.ignorewords.split()
            self.ignorewords = ' '.join([word for word in words if word != word_to_remove])
        else:
            words = self.filter_words.split()
            self.filter_words = ' '.join([word for word in words if word != word_to_remove])


room_id = '653a204cd2ba9c946594d95d'
api_key = '7bfb8522233ce607a7cae399c640e9867d4f4351bae7553b66490838a348659e'

if __name__ == "__main__":
    while True:
        try:
            arun(main(
                [
                    BotDefinition(
                        ModeratorBot(),
                        room_id,
                        api_key)
                ]
            )
            )
        except Exception as e:
            import traceback

            print("Caught an exception:")
            traceback.print_exc()  # This will print the full traceback
            continue
