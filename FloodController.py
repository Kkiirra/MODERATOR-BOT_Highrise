import time

class ChatFloodController:
    def __init__(self, flood_limit=5, flood_period=10):
        self.flood_limit = flood_limit  # Максимальное количество сообщений
        self.flood_period = flood_period  # Период времени в секундах
        self.messages = {}  # Словарь для отслеживания сообщений каждого пользователя

    def is_flooding(self, user_id):
        current_time = time.time()
        if user_id in self.messages:
            user_messages = self.messages[user_id]
            # Проверяем количество сообщений и время последнего сообщения
            if len(user_messages) >= self.flood_limit and current_time - user_messages[-1][0] < self.flood_period:
                return True
        return False

    def add_message(self, user_id, message):
        current_time = time.time()
        if user_id in self.messages:
            self.messages[user_id].append((current_time, message))
        else:
            self.messages[user_id] = [(current_time, message)]

# Пример использования
flood_controller = ChatFloodController()

def send_message(user_id, message):
    if flood_controller.is_flooding(user_id):
        print("Flood control triggered for user {}. Please wait before sending another message.".format(user_id))
    else:
        flood_controller.add_message(user_id, message)
        print("Message sent for user {}: {}".format(user_id, message))

# Теперь можно вызывать send_message() для отправки сообщений, и flood_controller автоматически управляет затоплением.
