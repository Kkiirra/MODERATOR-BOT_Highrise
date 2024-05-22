class BaseModeratorBot:
    async def welcome_onoff(self, user: User, choice: str, response: httpx.Response = None) -> None:
        if choice in self.CHOICES:
            try:
                response = await self.http_request(
                    method='PUT', url=self.API_BOTS,
                    data={
                        "api_key": self.api_key,
                        "welcome": self.CHOICES[choice]
                    }
                )
            except httpx.HTTPStatusError:
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время изменения")

            if response:
                await self.whisper_to_user(user, f"Функция приветствия изменена")
                self.welcome = response.get('welcome')
            else:
                await self.whisper_to_user(user, f"ServerError: Ошибка во время отправки запроса")

        else:
            await self.whisper_to_user(user, f"Выберите между on/off")

    async def set_welcome_message(self, user: User, message: str, response: httpx.Response = None) -> None:
        try:
            response = await self.http_request(
                method='PUT', url=self.API_BOTS,
                data={
                    "api_key": self.api_key,
                    "set_welcome": message
                }
            )
        except (httpx.HTTPStatusError, httpx.WriteError):
            await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

        if response:
            await self.whisper_to_user(user, f"Приветствие изменено")
            self.set_welcome = response.get('set_welcome')

    async def ban_user(self, user: User, username_lenght: str) -> None:

        try:
            username, lenght = username_lenght.split(maxsplit=1)
        except ValueError:
            await self.whisper_to_user(user, f"ValueError: Ошибка, пример /m ban Kkiirra2 10")
            return

        if lenght.isdigit():
            user_id = await self.get_user(username)

            try:
                await self.highrise.moderate_room(user_id, 'ban', int(lenght) * 3600)
            except highrise.ResponseError:
                await self.whisper_to_user(user, f"Пользователь не найден.")
                return
            await self.whisper_to_user(user, f"Пользователь {username} забанен на {lenght} часов")
        else:
            await self.whisper_to_user(user, f"ValueError: Ошибка, пример /m ban Kkiirra2 10")

    async def unban_user(self, user: User, username) -> None:

        user_id = await self.get_user(username)

        try:
            await self.highrise.moderate_room(user_id, 'unban')
        except highrise.ResponseError:
            await self.whisper_to_user(user, f"Пользователь не найден.")
            return
        await self.whisper_to_user(user, f"Пользователь {username} разбанен")

    async def mute_user(self, user: User, username_lenght: str) -> None:

        try:
            username, lenght = username_lenght.split(maxsplit=1)
        except ValueError:
            await self.whisper_to_user(user, f"ValueError: Ошибка, пример /m mute Kkiirra2 10")
            return

        if lenght.isdigit():
            user_id = await self.get_user(username)

            try:
                await self.highrise.moderate_room(user_id, 'mute', int(lenght) * 3600)
            except highrise.ResponseError:
                await self.whisper_to_user(user, f"Пользователь не найден.")
                return

            await self.whisper_to_user(user, f"Пользователь {username} заглушен на {lenght} часов")
            await self.highrise.send_whisper(user_id, f'Вы получили мут на 10 часов от {user.username}')
        else:
            await self.whisper_to_user(user, f"ValueError: Ошибка, пример /m mute Kkiirra2 10")

    async def unmute_user(self, user: User, username) -> None:

        user_id = await self.get_user(username)

        try:
            await self.highrise.moderate_room(user_id, 'mute', 1)
        except highrise.ResponseError:
            await self.whisper_to_user(user, f"Пользователь не найден.")
            return

        await self.whisper_to_user(user, f"Пользователь {username} размучен")
        await self.highrise.send_whisper(user_id, f'Вы получили размут от {user.username}')

    async def kick_user(self, user: User, username: str) -> None:

        user_id = await self.get_user(username)

        try:
            await self.highrise.moderate_room(user_id, 'kick')
        except highrise.ResponseError:
            await self.whisper_to_user(user, f"Пользователь не найден.")
            return
        await self.whisper_to_user(user, f"Пользователь {username} выгнан из комнаты.")

    async def warn_user(self, user: User, username_reason: str) -> None:

        try:
            username, reason = username_reason.split(maxsplit=1)
        except ValueError:
            await self.whisper_to_user(user, f"ValueError: Ошибка, пример /m warn Kkiirra2 Нецензурная брань")
            return

        user_id = await self.get_user(username)

        self.warnings.setdefault(username, {'count': 0, 'last_warning_time': datetime.now(),
                                            'user_id': user_id})['count'] += 1

        await self.highrise.send_whisper(user_id, f"Вы получаете предупреждение "
                                                  f"{self.warnings[username]['count']}/{self.warnlimit} "
                                                  f"\n\nПо причине: {reason}"
                                                  f"\n\nПосле {self.warnlimit} warns {self.warnmode} "
                                                  f"на {self.mute_duration} часа")

        await self.highrise.send_emote('emoji-angry')

        if self.warnings[username]['count'] >= self.warnlimit:
            self.warnings[username]['count'] = 0

            if self.warnmode == 'kick':
                await self.highrise.moderate_room(user_id, self.warnmode)
            elif self.warnmode == 'mute':
                await self.whisper_to_user(user_id, f'За неоднократное нарушение правил, '
                                                    f'вы получаете мут на '
                                                    f'{self.mute_duration} часов.')
                await self.highrise.moderate_room(user_id, self.warnmode, self.mute_duration * 3600)

            else:
                await self.highrise.moderate_room(user_id, self.warnmode, self.mute_duration * 3600)

    async def show_warnings(self, user: User, args: str):
        users_warnings = str()
        if self.warnings.values():
            for username, data in self.warnings.items():
                users_warnings += f"\nUsername: {username} Count: {data.get('count')}"
            await self.whisper_to_user(user, users_warnings)
        else:
            await self.whisper_to_user(user, 'Нету активных предупреждений')

    async def reset_warning(self, user: User, username: str):
        self.warnings[username]['count'] = 0
        await self.whisper_to_user(user, f"Предупреждения для {username} сброшены.")

    async def reset_all_warnings(self, user: User, args: str):
        for username in self.warnings.keys():
            self.warnings[username]['count'] = 0
        await self.whisper_to_user(user, f"Предупреждения для всех пользователей сброшены.")

    async def change_warnmode(self, user: User, warnmode: str, response: httpx.Response = None) -> None:
        if warnmode in self.MODE_INSTANCES:
            try:
                response = await self.http_request(
                    method='PUT', url=self.API_BOTS,
                    data={
                        "api_key": self.api_key,
                        "warnmode": warnmode
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Варн мод изменён")
                self.warnmode = response.get('warnmode')
        else:
            await self.whisper_to_user(user, f"Выберите между <ban/kick/mute>")

    async def change_warnlimit(self, user: User, warnlimit: str, response: httpx.Response = None) -> None:
        if warnlimit.isdigit():
            try:
                response = await self.http_request(
                    method='PUT', url=self.API_BOTS,
                    data={
                        "api_key": self.api_key,
                        "warnlimit": warnlimit
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Лимит предупреждений изменён")
                self.warnmode = response.get('warnlimit')
        else:
            await self.whisper_to_user(user, f"Неправильный ввод. \nПример: /m warnlimit 5")

    async def change_defaultfilter(self, user: User, choice: str, response: httpx.Response = None) -> None:
        if choice in self.CHOICES:
            try:
                response = await self.http_request(
                    method='PUT', url=self.API_BOTS,
                    data={
                        "api_key": self.api_key,
                        "defaultfilter": self.CHOICES[choice]
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Фильтр по умолчанию {choice}")
                self.warnmode = response.get('warnlimit')
        else:
            await self.whisper_to_user(user, f"Неправильный ввод. \nПример: /m defaultfilter <on/off>")

    async def list_filters(self, user: User, args: str, response: httpx.Response = None) -> None:
        await self.whisper_to_user(user, f"Filters: {self.filter_words}")

    async def add_filter(self, user: User, trigger: str, response: httpx.Response = None) -> None:
        if trigger:
            try:
                response = await self.http_request(
                    method='PUT', url=self.API_BOTS,
                    data={
                        "api_key": self.api_key,
                        "filter_words": trigger
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Добавлен новый фильтр {trigger}")
                self.filter_words = response.get('filter_words')
        else:
            await self.whisper_to_user(user, f"Ошибка. \nПример /m filter плохое слово.")

    async def delete_filter(self, user: User, trigger: str, response: httpx.Response = None) -> None:
        if trigger:
            try:
                response = await self.http_request(
                    method='DELETE', url=self.API_BOTS,
                    params={
                        "api_key": self.api_key,
                        "word": trigger,
                        "field": "filter_words"
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Фильтр {trigger} удалён")
                await self.remove_word_from_string('filter_words', trigger)
        else:
            await self.whisper_to_user(user, f"Ошибка. \nПример /m dfilter плохое слово")

    async def ignore_words(self, user: User, args: str, response: httpx.Response = None) -> None:
        await self.whisper_to_user(user, f"Ignore words list: {self.ignorewords}")

    async def add_ignore(self, user: User, trigger: str, response: httpx.Response = None) -> None:
        if trigger:
            try:
                response = await self.http_request(
                    method='PUT', url=self.API_BOTS,
                    data={
                        "api_key": self.api_key,
                        "ignorewords": trigger
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Добавлен новый игнор {trigger}")
                self.ignorewords = response.get('ignorewords')
        else:
            await self.whisper_to_user(user, f"Ошибка. \nПример /m ignore слово.")

    async def delete_ignore(self, user: User, trigger: str, response: httpx.Response = None) -> None:
        if trigger:
            try:
                response = await self.http_request(
                    method='DELETE', url=self.API_BOTS,
                    params={
                        "api_key": self.api_key,
                        "word": trigger,
                        "field": "ignorewords"
                    }
                )
            except (httpx.HTTPStatusError, httpx.WriteError):
                await self.whisper_to_user(user, f"HTTPStatusError: Ошибка во время отправки запроса")

            if response:
                await self.whisper_to_user(user, f"Игнор {trigger} удалён")
                await self.remove_word_from_string('ignorewords', trigger)
        else:
            await self.whisper_to_user(user, f"Ошибка. \nПример /m dignore плохое слово")

    async def show_help(self, user: User, args: str):
        help_message = ' '.join(self.COMMAND_INSTRUCTIONS)
        max_length = 200

        for i in range(0, len(help_message), max_length):
            await self.whisper_to_user(user, help_message[i:i + max_length])

    async def whisper_to_user(self, user: User, message: str) -> None:
        """Whispers a message to a user."""
        await self.highrise.send_whisper(user.id, message)

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

    async def get_user(self, username):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://webapi.highrise.game/users?username={username}", )
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