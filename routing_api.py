from libs.route_planing import RoutePlaner
from libs.next_step import *
from libs.check_state import *
from libs.enkel_app import *
from libs.check_update import check_updates
from libs.gerda import Gerda_Assistent
from libs.chat import Chat

from libs.utils.api_requests import *
from flask import Flask, jsonify

import json
app = Flask(__name__)


@app.route('/api/route/<routing_infos>', methods=['GET'])
def routing(routing_infos):
    
    # clear route infos
    user_id, dep_name, arr_name,date_time = get_call_values(["user_id", "dep_name", "arr_name", "date_time"],
                                                           routing_infos, print_dict = True)
    
    dep_is_lat_lon = "0"
    route_planer = RoutePlaner(dep_name, arr_name, date_time, user_id, dep_is_lat_lon)
    
    route_json = route_planer.get_route()

    return route_json 


@app.route('/api/get_next_step/<next_step_infos>', methods=['GET'])
def next_step(next_step_infos):
    
    # clear route infos
    user_id, track_id, current_step = get_call_values(["user_id", "track_id", "current_step"],
                                                           next_step_infos, print_dict = True)

    next_step_json = get_next_step(user_id, track_id, current_step)
    
    return next_step_json 


@app.route('/api/check_state/<state_info>', methods=['GET'])
def check_state(state_info):
    
    # clear route infos
    user_id, track_id, lat, lon, current_step = get_call_values(["user_id", "track_id","lat","lon", "current_step"],
                                                           state_info, print_dict = True)
    


    
    user_state = State_Checker(user_id, track_id,lat,lon,current_step)
    
    is_on_track = user_state.check_on_track()
    is_on_time = user_state.check_on_time()
    is_dep_time = user_state.check_dep_time()
    is_arv_time = user_state.check_arv_time()
    is_route_update = user_state.check_route_update()
    is_next_station = user_state.check_near_station()
    is_final_destination = user_state.check_final_destination()
    is_new_message = user_state.check_new_message("Gerda_User")
    is_interaction, interaction_id, interaction_text = user_state.get_interaction (is_on_track, is_on_time, 
                                                                                   is_dep_time, is_arv_time,
                                                                                   is_route_update, is_next_station, 
                                                                                   is_final_destination, is_new_message)
    
    state = pd.Series([is_on_track, is_on_time, is_route_update, is_next_station, is_final_destination, is_interaction, interaction_id, interaction_text],
             index = ["is_on_track", "is_on_time", "is_route_update", "is_next_station", "is_final_destination", "is_interaction", "interaction_id", "interaction_text"])
    
    return state.to_json() 

@app.route('/api/check_update/<user_track_info>', methods=['GET'])
def check_update_route(user_track_info):
    user_id, track_id = get_call_values(["user_id", "track_id"],
                                        user_track_info, print_dict = True)
    
    
    return check_updates(user_id, track_id)




@app.route('/api/gerda_interaction/<user_info>', methods=['GET'])
def interaction(user_info):

    text, user_id, track_id, current_step, interaction_id = get_call_values(["text","user_id", "track_id", "current_step", "interaction_id"],
                                                           user_info, print_dict = True)

    gerda = Gerda_Assistent()
    
    if not interaction_id:
        interaction_id = "none"
        
    text_answer, interaction_id, is_interaction = gerda.assistent_interaction(text = text,name = "Gerda_User", interaction_id = interaction_id, user_id = user_id, track_id = track_id, current_step = current_step)

    interaction_answer = {'text': text_answer,
        'interaction_id': interaction_id,
        'is_interaction': is_interaction}
    
    return json.dumps(interaction_answer)


# In[2]:


@app.route('/api/chat/post/<info>', methods=['GET'])
def chat_post(info):
    user_id, track_id, name, text = get_call_values(["user_id", "track_id", "name", "text"],
                                        info, print_dict = True)
    key = user_id + "-" + track_id
    chat = Chat(key)
    res = chat.post_message(name, text)
    
    return res

@app.route('/api/chat/get/<info>', methods=['GET'])
def chat_get(info):
    user_id, track_id,name, get_all = get_call_values(["user_id", "track_id","name", "get_all"],
                                        info, print_dict = True)
    key = user_id + "-" + track_id
    chat = Chat(key)
    res = chat.get_message(get_all = get_all, name = name)
    
    return res

@app.route('/api/gerda_yes_no/<text>', methods=['GET'])
def yes_no(text):
    gerda = Gerda_Assistent()
    basic_answer = gerda.get_basic_answer(text)
    return basic_answer

@app.route('/api/01/get_user_route/<user_track_info>', methods=['GET'])
def get_user_route(user_track_info):
    user_id, track_id = get_call_values(["user_id", "track_id"],
                                        user_track_info, print_dict = True)
    
    return e_get_user_route(user_id, track_id)

@app.route('/api/01/get_user_pos/<user_track_info>', methods=['GET'])
def get_user_pos(user_track_info):
    user_id, track_id = get_call_values(["user_id", "track_id"],
                                        user_track_info, print_dict = True)
    
    return e_get_user_state(user_id,track_id)



if __name__ == '__main__':
    app.run(host= '0.0.0.0', port = 5001, debug=False)



