import redis
import json
import pytz
import numpy as np

from datetime import datetime



class Chat():
    
    def __init__(self, redis_key):
        self.r = redis.Redis(db=1)
        self.redis_key = redis_key
        
    def create_chat (self):

        user_data = {
            "messages":'[{"message_id" : -1,"name": "system","text": "nan", "datetime":"None"},{"message_id" : 0,"name": "system","text": "nan", "datetime":"None"}]',
            "user_resived": "system",
            }

        res = self.r.hmset(self.redis_key, user_data)
        self.r.expire(self.redis_key, 259200)
        return str(res)
    
    
    def post_message(self, name,text):
        text = text.replace("_", " ")
        chat_data = self.r.hgetall(self.redis_key)
        message = chat_data[b"messages"].decode("utf-8") 
        message =  message.replace("'", '"')
        # create dict from str 
        message = json.loads(message)

        # get new id
        new_message_id = message[-1]["message_id"] + 1 
        tz = pytz.timezone('Europe/Berlin')
            
        # set new message 
        new_message = {'message_id': new_message_id,
                       'name': name,
                       'text': text,
                       'datetime': str(datetime.now(tz))}
                                    
        # append new message
        message.append(new_message)

        user_data = {
            "messages": str(message),
            "user_resived": name,
            }

        res = self.r.hmset(self.redis_key, user_data)
        return '{"id":' + str(new_message_id) + ', "Not":0}'
    
    def get_message(self,get_all,name):
        
        if get_all == "1":
            chat_data = self.r.hget(self.redis_key, "messages")

            if chat_data is not None:
                message = chat_data.decode("utf-8") 
                message =  message.replace("'", '"')
                # create dict from str 
                res = json.loads(message)
            else:
                res = ""
        else:
            
            user_resived = self.r.hget(self.redis_key, "user_resived")
            user_resived = user_resived.decode("utf-8")
            user_resived = user_resived.split(" ")
     
            if np.isin(name, user_resived) == False:
                user_resived = ' '.join(user_resived)
                user_resived = user_resived + " " + name
                self.r.hset(self.redis_key, "user_resived", user_resived)
                
                chat_data = self.r.hget(self.redis_key, "messages")
                message = chat_data.decode("utf-8") 
                message =  message.replace("'", '"')
                # create dict from str 
                res = json.loads(message)


            else:
                res = '{"None": 0, "Not":0}'

        return str(res)

