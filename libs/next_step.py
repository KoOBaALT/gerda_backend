
# coding: utf-8

# In[35]:

import pandas as pd
from sqlalchemy import create_engine


#user_id = "Jochen_test"
#stage = "0"

def get_next_step (user_id, track_id, current_step):
    
    engine = create_engine('mysql+mysqlconnector://gerda_api:[db_password]@localhost/gerda_db')


    new_stage = int(current_step) + 1
    new_stage = str(new_stage)

    post_new_stage (user_id, new_stage)
    
    ### Add Track ID
    query = "SELECT all_stations_on_step,dep_lat,dep_lon,dep_platfrom, dep_name, arv_name, arv_lat,arv_lon,arv_platfrom,transport_type,transporter_name,transporter_direction, dep_time, arv_time, step_polyline,step_maneuver,stage FROM routes WHERE user_id ='"+ user_id+ "' AND track_id='"+ track_id + "'AND stage = '"+ new_stage +"';"

    next_stage = pd.read_sql(sql = query, con = engine)
    engine.dispose()
    
    next_stage_json  = next_stage.iloc[0,:].to_json()
    
    return next_stage_json

def post_new_stage(user_id, new_stage):
    # dummy for user travel table
    
    #update table
    
    return True
    

