import pandas as pd
import redis
import json 

from sqlalchemy import create_engine

def e_get_user_state (user_id,track_id):
    redis_key = user_id + "-" + track_id
    r = redis.Redis(charset="utf-8", decode_responses=True)

    dic_user = r.hgetall(redis_key)

    return  json.dumps(dic_user)

def e_get_user_route (user_id, track_id):
    engine = create_engine('mysql+mysqlconnector://gerda_api:[db_password]@localhost/gerda_db')

    query = "SELECT dep_name,dep_time, arv_name,arv_time, transport_type, step_polyline FROM routes WHERE user_id ='" + user_id + "' AND track_id = '" + track_id + "'"

    data_route = pd.read_sql(sql=query, con=engine)
   
    engine.dispose()
    
    return  data_route.to_json()

def e_get_chat (user_id,track_id):
    
    
    return  data_route.to_json()

def post_chat_message(user_id, track_id, name, text):
    
    return None
