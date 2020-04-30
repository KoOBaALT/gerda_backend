
# coding: utf-8

# In[69]:

import numpy as np
import pandas as pd 
import geocoder
import json
import requests
from sqlalchemy import types, create_engine
from sqlalchemy.dialects.mysql import LONGTEXT
import uuid
import ast

"""

Testing Example of the Functions


  

"""
class RoutePlaner ():

    
    
    
    def __init__ (self, dep_place_name,arr_place_name, date_time, user_id, dep_is_lat_lon):
        self.dep_place_name = dep_place_name
        self.arr_place_name = arr_place_name
        self.date_time = date_time
        self.user_id = user_id
        self.dep_is_lat_lon = dep_is_lat_lon
        
        self.lat_dep = None
        self.lon_dep = None
        self.lat_arv = None
        self.lon_arv = None
        
        self.is_error = [0,0]
        self.error_info = ""
                  
                  
    def _get_lat_lon (self, place_name):

        # get geocode postion
        g = geocoder.osm(place_name)
       
        if g.ok == True:
            lat = g.json ["lat"]
            lon = g.json ["lng"]
            
        else:
            lat = 0.0
            lon = 0.0
            print("No LatLon")
            self.is_error[0] = 1
            self.error_info = self.error_info + " " + 'Place ' + place_name + ' not found'

        return(str(lat),str(lon))

    
    

    def _get_route_raw (self):
        
        if self.dep_is_lat_lon == "0":
            self.lat_dep, self.lon_dep = self._get_lat_lon(str(self.dep_place_name))
        elif self.dep_is_lat_lon == "1":
            self.lat_dep, self.lon_dep = str(self.dep_place_name).split(" ")
            #print(self.lat_dep, self.lon_dep)
            
        self.lat_arv, self.lon_arv = self._get_lat_lon(str(self.arr_place_name))


        if np.sum(self.is_error) == 0: # if no error in places
            

            request = "https://transit.api.here.com/v3/route.json?app_id=[api_key]&routing=all&graph=1&max=1&maneuvers=1&max_distance=500,speed=75,secCtx=1&arr="+ self.lat_arv+ ","+ self.lon_arv + "&time="+self.date_time+"&lang=de&dep="+ self.lat_dep +","+self.lon_dep
            
            
            result = requests.get(request)
          
            if not np.isin("Message", list(result.json() ["Res"].keys())): # if no error in request

                return result.json()
            else:
                
                self.is_error[1] = 1
                self.error_info = self.error_info + " " + result.json() ["Res"] ["Message"]["text"]

                return result.json()  
        else:
            return None
        

    def _preprocessing_new_route (self, raw_json):
        if np.sum(self.is_error) == 0:
            data_route_raw = raw_json["Res"]["Connections"]["Connection"][0]["Sections"]["Sec"]

            manover_data = raw_json["Res"]["Guidance"]["Maneuvers"]
            manover_ids = np.array([manover_data[i]["sec_ids"] for i in range(len(manover_data))])

            data_route = pd.DataFrame(columns = ["transport_type","dep_time", "dep_lat", "dep_lon","dep_name","dep_platfrom", "dep_transport", "transporter_name", "transporter_direction",
                      "arv_time","arv_lat", "arv_lon", "arv_name", "arv_platfrom",
                      "step_duration", "step_distance","step_polyline", "step_maneuver", "all_stations_on_step", "alternative_steps", "step_update_id"])


            for i in range(len(data_route_raw)):

                # Set Null
                dep_name = "None"


                if np.isin("time", list(data_route_raw[i]["Dep"].keys())):
                    dep_time = data_route_raw[i]["Dep"]["time"]
                else:
                    dep_time = "None"

                #Addr Dep
                if np.isin("Addr", list(data_route_raw[i]["Dep"].keys())):

                    if np.isin("x", list(data_route_raw[i]["Dep"]["Addr"].keys())):
                        dep_lat = data_route_raw[i]["Dep"]["Addr"]["y"]
                    else:
                        dep_lat = "None"


                    if np.isin("y", list(data_route_raw[i]["Dep"]["Addr"].keys())):
                        dep_lon = data_route_raw[i]["Dep"]["Addr"]["x"]
                    else:
                        dep_lon = "None"


                if np.isin("time", list(data_route_raw[i]["Dep"].keys())):
                    dep_time = data_route_raw[i]["Dep"]["time"]
                else:
                    dep_time = "None"


                if np.isin("mode", list(data_route_raw[i]["Dep"]["Transport"].keys())):
                    dep_transport = data_route_raw[i]["Dep"]["Transport"]["mode"]
                else:
                    dep_transport = "None"   


                if np.isin("time", list(data_route_raw[i]["Arr"].keys())):
                    arv_time = data_route_raw[i]["Arr"]["time"]
                else:
                    arv_time = "None"   

                #Station Dep
                if np.isin("Stn", list(data_route_raw[i]["Dep"].keys())):

                    if np.isin("x", list(data_route_raw[i]["Dep"]["Stn"].keys())):
                        dep_lat = data_route_raw[i]["Dep"]["Stn"]["y"]
                    else:
                        dep_lat = "None"   


                    if np.isin("y", list(data_route_raw[i]["Dep"]["Stn"].keys())):
                        dep_lon = data_route_raw[i]["Dep"]["Stn"]["x"]
                    else:
                        dep_lon = "None"   


                    if np.isin("name", list(data_route_raw[i]["Dep"]["Stn"].keys())):
                        dep_name = data_route_raw[i]["Dep"]["Stn"]["name"]
                    else:
                        dep_name = "None"
                
                #Gleisinfos
                if np.isin("platform", list(data_route_raw[i]["Dep"].keys())):
                        dep_platfrom = data_route_raw[i]["Dep"]["platform"]
                else:
                        dep_platfrom = "None"                        
                    
                if np.isin("platform", list(data_route_raw[i]["Arr"].keys())):
                        arv_platfrom = data_route_raw[i]["Arr"]["platform"]
                else:
                        arv_platfrom = "None"     

                if np.isin("dir", list(data_route_raw [i]["Dep"]["Transport"].keys())):      
                    transporter_direction = data_route_raw [i]["Dep"]["Transport"]["dir"]       
                else:
                    transporter_direction = "None"


                if np.isin("name", list(data_route_raw [i]["Dep"]["Transport"].keys())):      
                    transporter_name = data_route_raw [i]["Dep"]["Transport"]["name"]       
                else:
                    transporter_name = "None"


                if np.isin("Stn", list(data_route_raw[i]["Arr"].keys())):

                    if np.isin("x", list(data_route_raw[i]["Arr"]["Stn"].keys())):
                        arv_lat = data_route_raw[i]["Arr"]["Stn"]["y"]
                    else:
                        arv_lat = "None"   


                    if np.isin("y", list(data_route_raw[i]["Arr"]["Stn"].keys())):
                        arv_lon = data_route_raw[i]["Arr"]["Stn"]["x"]
                    else:
                        arv_lon = "None"   


                    if np.isin("name", list(data_route_raw[i]["Arr"]["Stn"].keys())):
                        arv_name = data_route_raw[i]["Arr"]["Stn"]["name"]
                    else:
                        arv_name = "None"  


                if np.isin("duration", list(data_route_raw[i]["Journey"].keys())):
                    step_duration = data_route_raw[i]["Journey"]["duration"]
                else:
                    step_duration = "None" 


                if np.isin("distance", list(data_route_raw[i]["Journey"].keys())):
                    step_distance = data_route_raw[i]["Journey"]["distance"]
                else:
                    step_distance = "None" 


                # Stop auf der Strecke
                if np.isin("Stop", list(data_route_raw[i]["Journey"].keys())):
                    stops = ""
                    for stop in data_route_raw[i]["Journey"]["Stop"]:
                        if np.isin("dep", list(stop.keys())):
                            stop_dep =  stop ["dep"]
                        elif  np.isin("arr", list(stop.keys())):
                            stop_dep = stop ["arr"]
                        else:
                            stop_dep = "None"


                        name_stop =   stop ["Stn"]["name"]
                        stop_lat =   stop ["Stn"]["y"]
                        stop_lon =   stop ["Stn"]["x"]

                        stop_temp = str(name_stop) + "," + str(stop_lat) + "," + str(stop_lon) + ","  + stop_dep +";"
                        stops = stops + stop_temp

                else:
                    stops = None


                #Alternativen


                if np.isin("Freq", list(data_route_raw[i]["Dep"].keys())):
                    if np.isin("AltDep", list(data_route_raw[i]["Dep"]["Freq"].keys())):

                        alternative_steps = ""

                        for alt in data_route_raw[i]["Dep"]["Freq"]["AltDep"]:

                            alt_name =   alt["Transport"]["name"]
                            alt_direction =   alt["Transport"]["dir"]
                            alt_mode =   alt["Transport"]["mode"]
                            alt_time = alt["time"]

                            alternativen_temp = str(alt_name) + "," + str(alt_direction) + "," + str(alt_time) + ","  + str(alt_mode) +";"
                            alternative_steps = alternative_steps + alternativen_temp

                else:
                    alternative_steps = None
                
                
                step_id = data_route_raw[i]["id"]
                step_maneuver = "None"
                
                if np.isin("graph", list(data_route_raw[i].keys())):
                    step_polyline = data_route_raw[i]["graph"]
                else:
                    if np.isin(step_id, manover_ids):
                        # get ployline fro graph
                        index_id = np.where(manover_ids == step_id)[0][0]
                        step_maneuver = manover_data [index_id]["Maneuver"]
                        polyline_transport = [step_maneuver[i]["graph"] for i in range(len(manover_data [index_id]["Maneuver"]))]
                        step_polyline = " ".join(polyline_transport)
                        step_maneuver = str(step_maneuver)
                        
                    else:
                        step_polyline = "None"
                    
                    
                if np.isin("At", list(data_route_raw [i]["Dep"]["Transport"].keys())):     
                    if np.isin("category", list(data_route_raw [i]["Dep"]["Transport"]["At"].keys())):      
                        transport_type = data_route_raw [i]["Dep"]["Transport"]["At"]["category"]   
                    else:
                        if step_maneuver == "None":
                            transport_type = "Umstieg"
                        else:
                            transport_type = "Laufen"
                else:
                    if step_maneuver == "None":
                            transport_type = "Umstieg"
                    else:
                            transport_type = "Laufen"
                    
                if np.isin("context", list(data_route_raw[i].keys())):
                    step_update_id = data_route_raw[i]["context"]
                else:    
                    step_update_id = None

                # If it is last station than get the arv_lat and arv_lon from the step_maneuver
                if i == (len(data_route_raw)-1) and transport_type == "Laufen":

                    split_man = ast.literal_eval(step_maneuver)
                    
                    new_lat_lon = split_man [-1]["graph"].split(",")
                    arv_lat = new_lat_lon [0]
                    arv_lon = new_lat_lon [1]
                    
                    
                temp_data_route = pd.Series([transport_type,dep_time, dep_lat, dep_lon,dep_name,dep_platfrom, dep_transport, transporter_name, transporter_direction,
                          arv_time,arv_lat, arv_lon, arv_name, arv_platfrom,
                          step_duration, step_distance, step_polyline,step_maneuver, stops, alternative_steps, step_update_id], 
                          index = ["transport_type","dep_time", "dep_lat", "dep_lon","dep_name","dep_platfrom","dep_transport", "transporter_name", "transporter_direction",
                          "arv_time","arv_lat", "arv_lon", "arv_name","arv_platfrom", 
                          "step_duration", "step_distance", "step_polyline","step_maneuver", "all_stations_on_step", "alternative_steps", "step_update_id"])   

                data_route = data_route.append (temp_data_route, ignore_index=True)


            data_route["stage"] = list(range(0,len(data_route)))
            return data_route
        
        else:
            return None


        
        
    def _post_new_route (self, data_new_route):
        if np.sum(self.is_error) == 0:
            # create connector object

            mydb = create_engine('mysql+mysqlconnector://gerda_api:[db_password]@localhost/gerda_db')

            # generate track_id
            track_id = str(uuid.uuid1()).replace("-", "_")

            # add IDs
            data_new_route["user_id"] = self.user_id
            data_new_route["track_id"] = track_id


            # post data to gerda_db
            data_new_route.to_sql(con=mydb, name='routes', if_exists='append', flavor='mysql', dtype = {"step_polyline": LONGTEXT, "all_stations_on_step": LONGTEXT, "alternative_steps": LONGTEXT, "step_distance": types.String(40) , "step_maneuver": LONGTEXT})
            
            # close connection 
            
            mydb.dispose()
            
            # sending user less data
            data_prep_json = data_new_route[["track_id","dep_name","dep_time", "arv_name","arv_time", "transport_type"]]
            data_prep_json ["dep_name"].iloc[0] = self.dep_place_name
            data_prep_json = data_prep_json.to_json(orient = "records")

            return data_prep_json
        
        # if there was an error in routing process
        else:
            error_response = "[{error_code=" + str(self.is_error) + ",error_text=" + str(self.error_info) + "}]"
            return str(error_response)
            
            
            
    def get_route(self):
        
        self.is_error = [0,0]
        self.error_info = ""
        
        # get raw route data
        raw_data = self._get_route_raw()

        # preprocessing raw data
        data_temp = self._preprocessing_new_route(raw_data)

        # route infos to json
        routing_output_json = self._post_new_route(data_temp)

        return routing_output_json

