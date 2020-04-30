import numpy as np
import pandas as pd
import redis
import pytz
import json

from geopy.distance import distance
from sqlalchemy import create_engine
from datetime import datetime

from libs.chat import Chat

class State_Checker():

    def __init__(self, user_id, track_id, lat, lon, current_step):
        self.user_id = user_id
        self.track_id = track_id
        self.lat = lat
        self.lon = lon
        self.current_step = current_step
        self.is_final_stage = False
        self.message = ""

        # create SQL-Connectionobject
        self.engine = create_engine('mysql+mysqlconnector://gerda_api:[db_password]@localhost/gerda_db')

        # update Redis
        self.redis_key = self.user_id + "-" + self.track_id
        r = redis.Redis(charset="utf-8", decode_responses=True)

        tz = pytz.timezone('Europe/Berlin')

        user_data = {
            "lat": self.lat,
            "lon": self.lon,
            "current_state": self.current_step,
            "time": str(datetime.now(tz))
        }

        r.hmset(self.redis_key, user_data)

    def get_next_stop_station(self):

        query = "SELECT all_stations_on_step FROM routes WHERE user_id ='" + self.user_id + "' AND stage ='" + self.current_step + "' AND track_id = '" + self.track_id + "'"

        data = pd.read_sql(sql=query, con=self.engine).values[0]

        if data[0] is not None:

            station_exit = data[0].split(";")[-2].split(",")[0]

        else:
            station_exit = ""

        return station_exit

    
    
    def check_new_message(self, name):
        is_new_message = False
        chat = Chat(self.redis_key)
        res = chat.get_message(get_all = "0", name = name)
        
        if res == '{"None": 0, "Not":0}':
            is_new_message = False
        
        else:
            is_new_message = True
            self.message = res.replace("'", '"')
            self.message = json.loads(self.message)
            self.message_text = self.message [-1]["text"]
            if self.message_text == "nan":
                is_new_message = False
            self.message_name = self.message [-1]["name"]

        return is_new_message
    
    
    
    
    def check_on_track(self):

        return True

    def check_on_time(self):

        return True

    def check_dep_time(self):

        is_dep_time = False


        query = "SELECT dep_time, transport_type FROM routes WHERE user_id ='" + self.user_id + "' AND stage ='" + self.current_step + "' AND track_id = '" + self.track_id + "'"
        info_dep = pd.read_sql(sql=query, con=self.engine).values[0]

        # Dep Time and now time
        time_diff = datetime.strptime((str(info_dep[0])), "%Y-%m-%dT%H:%M:%S") - datetime.now()
        time_diff = time_diff.seconds / 60 - 60  # Timezone +1

        print(time_diff)
        if time_diff < 1 and info_dep[1] != "Laufen":
            is_dep_time = True

        return is_dep_time

    def check_arv_time(self):
        is_arv_time = False

        query = "SELECT arv_time, transport_type FROM routes WHERE user_id ='" + self.user_id + "' AND stage ='" + self.current_step + "' AND track_id = '" + self.track_id + "'"
        info_arv = pd.read_sql(sql=query, con=self.engine).values[0]

        # Dep Time and now time
        time_diff = datetime.strptime((str(info_arv[0])), "%Y-%m-%dT%H:%M:%S") - datetime.now()
        time_diff = time_diff.seconds / 60 - 60  # Timezone +1

        print(time_diff)
        if time_diff < 1.5 and info_arv[1] != "Laufen":
            is_arv_time = True

        return is_arv_time

    def check_route_update(self):

        return False

    def check_near_station(self):

        query = "SELECT arv_lat,arv_lon FROM routes WHERE user_id ='" + self.user_id + "' AND stage ='" + self.current_step + "' AND track_id = '" + self.track_id + "'"

        lat_lon_arv_station = pd.read_sql(sql=query, con=self.engine).values[0]

        lat = lat_lon_arv_station[0]
        lon = lat_lon_arv_station[1]
        coord_next_station = [lat, lon]

        coord_user = [self.lat, self.lon]

        dist = distance(coord_next_station, coord_user).m

        if dist < 150:
            near_next_staion = True
        else:
            near_next_staion = False

        return near_next_staion

    def check_final_destination(self):

        is_final_destination = False


        query = "SELECT arv_lat,arv_lon FROM routes WHERE user_id ='" + self.user_id + "' AND track_id = '" + self.track_id + "'"

        stages = pd.read_sql(sql=query, con=self.engine).values

        if (len(stages) - 1) == int(self.current_step):
            self.is_final_stage = True
            lat = stages[int(self.current_step), 0]
            lon = stages[int(self.current_step), 1]
            coord_next_station = [lat, lon]

            coord_user = [self.lat, self.lon]

            dist = distance(coord_next_station, coord_user).m

            if dist < 50:
                is_final_destination = True
            else:
                is_final_destination = False

        else:

            is_final_destination = False

        return is_final_destination

    def get_interaction(self, is_on_track, is_on_time, is_dep_time, is_arv_time, is_route_update, is_next_station,
                        is_final_destination, is_new_message):
        is_interaction = False
        interaction_id = ""
        interaction_text = ""

        ##### Hier muss beahtete werden, was passiert, wenn jemand innerhalb 1,5 Minuten vor abfahrt an der Station ankommt ####

        
        if is_dep_time:
            is_interaction = True
            interaction_id = "dep_time_0"
            interaction_text = "Befindest du dich in deinem nächsten Transportmittel?"
            
        if is_arv_time:
            is_interaction = False
            interaction_id = "none"
            next_stop_station = self.get_next_stop_station()
            interaction_text = "Du erreicht in weniger als 2 Minuten die Haltestelle " + next_stop_station + ". Hier musst du aussteigen."

            
        if is_next_station and self.is_final_stage == False:
            is_interaction = True
            interaction_id = "near_next_station_0"
            interaction_text = "Bist du an der nächsten Station angekommen?"
            
        if is_final_destination:
            is_interaction = False
            interaction_id = "none"
            interaction_text = "Du hast es geschafft, du bist an deinem Ziel angekommen!"
        
        if is_new_message:
            is_interaction = True
            interaction_id = "new_message_0"
            interaction_text = "Du hast eine neue Nachricht, von " + self.message_name + ". Der Inhalt lautet: "+ self.message_text + ". Ende der Nachricht. Möchtest du darauf antworten?"
        
        
        self.engine.dispose()
        
        return is_interaction, interaction_id, interaction_text
