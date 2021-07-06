import telegram
import time
import yaml

class GotCourtsWaiterBot():
    def __init__(self, token:str, config_path:str):
        self.bot = telegram.Bot(token=token)
        self.config = self.get_config(config_path)
        
    def get_config(self, config_path:str):
        with open(config_path, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

    def message_all(self, text:str):
        for chat_id in self.config['chat_ids']:
            self.bot.send_message(chat_id=chat_id, text=text)