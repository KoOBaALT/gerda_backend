import pandas as pd
import redis
from libs.chat import Chat

def check_updates (user_id, track_id):
    redis_key = user_id + "-" + track_id
    r = redis.Redis(charset="utf-8", decode_responses=True)
    
    if r.exists (redis_key) == False:
        #Create new User_Track Key in Redis
        user_data = {
        "lat": 0.0,
        "lon": 0.0,
        "current_state": -1,
        "time": "00:00"
        }

        r.hmset(redis_key, user_data)
        r.expire(redis_key, 259200)
        
        # create chat data
        
        chat = Chat (redis_key = redis_key)
        chat.create_chat()
        
    is_route_ok = True
    route_info = ""
    return_updates = pd.Series ([is_route_ok,route_info], index= ["is_route_ok","route_info"])
    
    
    return  return_updates.to_json()