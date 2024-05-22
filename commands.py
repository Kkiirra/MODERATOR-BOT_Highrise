CM_INSTR = [
    "\nhelp - list all commands",
    "\nwelcome <on/off> - Активировать/Отключить приветствие",
    "\nsetwelcome <message> - Установить приветствие",

    "\nban <username> <time> - Забанить пользователя",
    "\nunban <username> - Разбанить пользователя",
    "\nmute <username> <lenght> - Замутить пользователя",
    "\nunmute <username> - Размутить пользователя",
    "\nkick <username> - Выгнать пользователя",

    "\nwarn <username> - Дать предупреждение",
    "\nwarns - Список предупреждений",
    "\nresetwarn <username> - Сбросить предупреждения пользователя до 0",
    "\nresetallwarn - Сбросить предупреждения всех пользователей",

    "\nwanrmode <ban/kick/mute> - Функция, которая сработает после пересечения лимита предупреждений ban/kick/mute",
    "\nwarnlimit <integer> - Лимит предупреждений",
    "\nwarntime <time> - Время жизни предупреждений",

    "\ndefaultfilter <on/off> - Включение/Выключение базовой фильтрации",
    "\nfilters - Список фильтров",
    "\nfilter <trigger> - Добавить фильтер",
    "\ndfilter <trigger> - Удалить фильтер",

    "\nignore <word> - Слово, которое будет игнорировать фильтрацию"
    "\ndignore <word> - Удалить слово, которое будет игнорировать фильтрацию"
    "\nignorewords - Список игнор слов"

]

MD_INST = ["mute", "kick", "ban"]
CH_INST = {
    "on": True,
    "off": False,
}
WELC_INST = "\nДобро пожаловать в нашу комнату. \n\n📜 Правила: /rules \n🤖 Помощь: /help"

MOD_PARAMS = ['welcome', 'set_welcome', 'mute_duration', 'warnmode', 'warnlimit',
              'warntime', 'defaultfilter', 'ignorewords', 'filter_words', 'banned']


def setup_commands(instance):
    return {
        'welcome': instance.welcome_onoff,
        'setwelcome': instance.set_welcome_message,
        'ban': instance.ban_user,
        'unban': instance.unban_user,
        'mute': instance.mute_user,
        'unmute': instance.unmute_user,
        'kick': instance.kick_user,
        'warn': instance.warn_user,  #
        'warns': instance.show_warnings,  #
        'resetwarn': instance.reset_warning,  #
        'resetallwarns': instance.reset_all_warnings,  #
        'warnmode': instance.change_warnmode,
        'warnlimit': instance.change_warnlimit,
        'defaultfilter': instance.change_defaultfilter,
        'filters': instance.list_filters,  #
        'filter': instance.add_filter,
        'dfilter': instance.delete_filter,
        'ignorewords': instance.ignore_words,  #
        'ignore': instance.add_ignore,
        'dignore': instance.delete_ignore,
        'help': instance.show_help  #
    }
