# coding: utf-8

# In[250]:

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from wit import Wit

from libs.chat import Chat

class Gerda_Assistent:

    def __init__(self):
        self.client_basic = Wit("[api_key]")
        self.client_basic_answer = Wit("[api_key]")
        self.client_basic_question = Wit("[api_key]")
        
        # create sql-conennction
        self.engine = create_engine('mysql+mysqlconnector://gerda_api:[db_password]@localhost/gerda_db')



    def get_basic_intention(self, text):

        message_result = self.client_basic.message(text)

        if "entities" in message_result:
            if "intent" in message_result["entities"]:
                intent = message_result["entities"]["intent"][0]["value"]
            else:
                intent = "na"

        else:
            intent = "na"

        return intent

    def get_basic_answer(self, text):
        answer_intent = self.client_basic_answer.message(text)

        if "entities" in answer_intent:
            if "intent" in answer_intent["entities"]:
                intent = answer_intent["entities"]["intent"][0]["value"]
            else:
                intent = "na"

        else:
            intent = "na"

        return intent

    def get_basic_question(self, text):
        answer_intent = self.client_basic_question.message(text)

        if "entities" in answer_intent:
            if "intent" in answer_intent["entities"]:
                intent = answer_intent["entities"]["intent"][0]["value"]
            else:
                intent = "na"

        else:
            intent = "na"

        return intent

    def get_next_dep_time(self, user_id, track_id, current_step):
        current_step = str(int(current_step) + 1)

        query = "SELECT dep_time,dep_name FROM routes WHERE user_id ='" + user_id + "' AND stage ='" + current_step + "' AND track_id = '" + track_id + "'"

        answer_data = pd.read_sql(sql=query, con=self.engine).values[0]

        dep_time = answer_data[0]

        answer_text = "Deine nächste Abfahrtszeit ist um " + dep_time[-8:-3] + " von " + answer_data[1]

        return answer_text

    def get_arv_current_step(self, user_id, track_id, current_step):

        query = "SELECT arv_name FROM routes WHERE user_id ='" + user_id + "' AND stage ='" + current_step + "' AND track_id = '" + track_id + "'"

        arv_name_current = pd.read_sql(sql=query, con=self.engine).values[0][0]

        return arv_name_current

    def get_dep_time_next_step(self, user_id, track_id, current_step):

        current_step = str(int(current_step) + 1)

        query = "SELECT dep_time FROM routes WHERE user_id ='" + user_id + "' AND stage ='" + current_step + "' AND track_id = '" + track_id + "'"

        dep_time_next = pd.read_sql(sql=query, con=self.engine).values[0]
        dep_time_next = str(dep_time_next).split("T")[1][:-5]
        return dep_time_next

    def get_arrived_message(self, user_id, track_id, current_step):

        current_step = str(int(current_step) + 1)

        query = "SELECT transport_type,dep_time,transporter_name,transporter_direction, arv_name, dep_platfrom  FROM routes WHERE user_id ='" + user_id + "' AND stage ='" + current_step + "' AND track_id = '" + track_id + "'"

        answer_data = pd.read_sql(sql=query, con=self.engine).values[0]

        fmt = '%Y-%m-%dT%H:%M:%S'
        d1 = datetime.strptime(answer_data[1], fmt)
        d2 = datetime.now()

        time_diff = (d1 - d2).seconds
        minutes = round(time_diff / 60) - 60  # Timezone +1

        # Update user state
        if answer_data[0] == "Bus" or answer_data[0] == "Intercity-Express":
            answer = "Sehr gut, als nächstes nimmst du den " + answer_data[0] + " mit der Bezeichnung " + answer_data[
                2] + " in Richtung " + answer_data[3] + ". Dein " + answer_data[0] + " fährt um " + str(d1.time())[
                                                                                                    :-3] + " Uhr ab. Du hast nun " + str(
                minutes) + " Minuten bis dein " + answer_data[0] + " abfährt."

        elif answer_data[0] == "S-Bahn":
            answer = "Sehr gut, als nächstes nimmst du die " + answer_data[0] + " mit der Bezeichnung " + answer_data[
                2] + " in Richtung " + answer_data[3] + ". Die " + answer_data[0] + " fährt um " + str(d1.time())[
                                                                                                   :-3] + " Uhr ab. Du hast nun " + str(
                minutes) + " Minuten bis deine " + answer_data[0] + " abfährt."

        elif answer_data[0] == "Laufen":
            answer = "Sehr gut, nun musst du zu deinem nächsten Zwischenziel laufen. Dieses heißst " + answer_data[
                4] + ". "

            if not answer_data[-1] == "None":
                answer = answer + " Dort musst du zu Gleisnummer" + answer_data[-1] + ". "

            answer = answer + "Ich führe dich als nun zu diesem nächsten Ziel. "

        else:
            answer = "Sehr gut, als nächstes nimmst du den " + answer_data[2] + " in Richtung " + answer_data[
                3] + ". Die Abfahrt ist um " + str(d1.time())[:-3] + " Uhr. Du hast nun " + str(
                minutes) + " Minuten bis zur Abfahrt"

        return answer

    def get_arrived_dep_time_message(self, user_id, track_id, current_step):

        current_step = str(current_step)

        query = "SELECT dep_time, arv_time, all_stations_on_step FROM routes WHERE user_id ='" + user_id + "' AND stage ='" + current_step + "' AND track_id = '" + track_id + "'"

        data = pd.read_sql(sql=query, con=self.engine).values[0]

        fmt = '%Y-%m-%dT%H:%M:%S'
        data[0] = datetime.strptime(data[0], fmt)
        data[1] = datetime.strptime(data[1], fmt)
        minutes_to_exit = round((data[1] - data[0]).seconds / 60)

        if data[2] != None:
            stations = len(data[2].split(";")) - 1
            station_exit = data[2].split(";")[-2].split(",")[0]

        else:
            stations = 0
            station_exit = ""

        answer = "Sehr gut, du fährst nun " + str(stations) + " Stationen und steigst dann bei der Haltestelle " + str(
            station_exit) + " aus. Du kannst dich nun für " + str(
            minutes_to_exit) + " Minuten entspannen. Ich melde mich bei dir, falls es Neuigkeiten gibt."

        return answer

    def assistent_interaction(self, name, text, interaction_id, user_id, track_id, current_step):
        # close connection
        self.engine.dispose()
        
        basic_intent = self.get_basic_intention(text)
        basic_answer_intent = self.get_basic_answer(text)
        
        
        # all questions 
        if basic_intent == "question":

            basic_question_intent = self.get_basic_question(text)

            if basic_question_intent == "arv_current_step":
                answer = self.get_arv_current_step(user_id, track_id, current_step)
                answer_text = "Der Name deines aktuellen Ziel lautet " + answer + "."
                answer_id = "is_question_answer"
                is_interaction = False

            if basic_question_intent == "dep_time_next_step":
                answer = self.get_dep_time_next_step(user_id, track_id, current_step)
                answer_text = "Der Zeitpunkt deiner nächsten Abfahrt ist um " + answer + " Uhr."
                answer_id = "is_question_answer"
                is_interaction = False

            if basic_question_intent == "na":

                return ["Deine Frage kenne ich noch nicht. Mach weiter so dann werde ich viel schlauer.", "none", False]

            else:
                return [answer_text, answer_id, is_interaction]


        elif basic_intent == "na" and interaction_id != "new_message_1":
            return ["Das habe ich leider nicht verstanden", interaction_id, True]

        # all interactiv dialogs 
        elif basic_intent == "answer" and basic_answer_intent != "na" or interaction_id == "new_message_1":

            # dep Route
            if interaction_id == "dep_time_0":

                if basic_answer_intent == "yes":
                    # User sits in next Trasnport unit
                    interaction_text = self.get_arrived_dep_time_message(user_id, track_id, current_step)
                    interaction_id = "arrived_in_transport_unit"
                    is_interaction = False

                if basic_answer_intent == "no":
                    # User sits in next Trasnport unit
                    interaction_text = "Ok alles klar, möchtest du mir bescheid geben, wenn du dich im Verkehrsmittel befindest?"
                    interaction_id = "dep_time_1"
                    is_interaction = True


            elif interaction_id == "dep_time_1":

                if basic_answer_intent == "yes":
                    # User sits in next Trasnport unit
                    interaction_text = "Ok wunderbar, dann warte ich auf deine Rückmeldung."
                    interaction_id = "dep_time_2"
                    is_interaction = False

                if basic_answer_intent == "no":
                    # User sits in next Trasnport unit
                    interaction_text = "Ok, dann werde ich versuchen anhand deiner Standort-Daten festzustellen, wann du losfährst."
                    interaction_id = "no_answer_dep_time"
                    is_interaction = False


            elif interaction_id == "dep_time_2":

                if basic_answer_intent == "yes":
                    # User sits in next Trasnport unit
                    interaction_text = self.get_arrived_dep_time_message(user_id, track_id, current_step)
                    interaction_id = "arrived_in_transport_unit"
                    is_interaction = False

                if basic_answer_intent == "no" or basic_answer_intent == "maybe":
                    interaction_text = "Falls du Hilfe benötigst, können wir dir Momentan leider nicht weiterhelfen. Frag ambesten jemand wie du zu deinem Ziel kommst."
                    interaction_id = "not_arrived_dep_time"
                    is_interaction = False

            # Near Station Route
            elif interaction_id == "near_next_station_0":

                if basic_answer_intent == "yes":
                    # User arrived at station

                    interaction_text = self.get_arrived_message(user_id, track_id, current_step)
                    interaction_id = "arrived_arv_station"
                    is_interaction = False

                elif basic_answer_intent == "no":
                    # User arrived at station

                    interaction_text = "Ok alles klar, möchtest du mir bescheid geben, wenn du angekommen bist?"
                    interaction_id = "near_next_station_1"
                    is_interaction = True



            elif interaction_id == "near_next_station_1":

                if basic_answer_intent == "yes":
                    interaction_text = "Wunderbar, dann warte ich auf deine Antwort. Bis gleich!"
                    interaction_id = "near_next_station_2"
                    is_interaction = False

                if basic_answer_intent == "no" or basic_answer_intent == "maybe":
                    interaction_text = "Alles klar! " + self.get_next_dep_time(user_id, track_id, current_step)
                    interaction_id = "no_answer_arrived_arv_station"
                    is_interaction = False


            elif interaction_id == "near_next_station_2":

                if basic_answer_intent == "yes":
                    interaction_text = self.get_arrived_message(user_id, track_id, current_step)
                    interaction_id = "arrived_arv_station"
                    is_interaction = False

                if basic_answer_intent == "no" or basic_answer_intent == "maybe":
                    interaction_text = "Falls du Hilfe benötigst, können wir dir Momentan leider nicht weiterhelfen. Frag ambesten jemand wie du zu deinem Ziel kommst."
                    interaction_id = "not_arrived_arv_station"
                    is_interaction = False
                    
                    
            elif interaction_id == "new_message_0":

                if basic_answer_intent == "yes":
                    # User sits in next Trasnport unit
                    interaction_text = "Alles klar, dann diktiere mir einfach die Nachricht und ich übermittel sie für dich."
                    interaction_id = "new_message_1"
                    is_interaction = True
                    
                if basic_answer_intent == "no" or basic_answer_intent == "maybe":
                    interaction_text = "Alles klar, dann melde dich bei mir, wenn du etwas brauchst."
                    interaction_id = "new_message_no_answer"
                    is_interaction = False    
            
            elif interaction_id == "new_message_1":
                redis_key = user_id + "-" + track_id
                chat = Chat(redis_key)
                chat.post_message(text = text, name = name)
                interaction_text = "Vielen Dank, ich habe die Nachricht gesendet."
                interaction_id = "new_message_2"
                is_interaction = False
                
            else:
                return ["Deine Antwort macht an dieser Stelle keinen Sinn. Schicke deine History an Jochen ;) ", "none",
                        False]

            # Final Return
            return [interaction_text, interaction_id, is_interaction]

        else:

            return ["Das habe ich leider nicht verstanden", interaction_id, True]

