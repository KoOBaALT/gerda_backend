import re
import numpy as np


def _clear_input(input_):
    # replace special charaters
    clear_input = input_.replace("%C3%9F", "ß")
    clear_input = clear_input.replace("%C3%A4", "ä")
    clear_input = clear_input.replace("%C3%BC", "ü")
    clear_input = clear_input.replace("C3%B6", "ö")
    
    # here all API clearning code
    clear_input = re.sub(r'[^a-zA-Z0-9.,=:_\-ßäüö]', '', clear_input)


    return clear_input

def _request_keys(keys, input_):
    
    request = {}
    
    input_splits = input_.split(",")
    
    for inputs in input_splits:
      
        key, value = inputs.split("=")
        if np.isin(key, ["arr_name", "dep_name"]):
            value = value.replace("_", " ")
        if key == "date_time":
            value = value.replace("_", "-")
            
        if np.isin(key, keys):
            request.update({key: value})
            
    return request

def get_call_values (keys, input_call, print_dict = False):
    
    input_call_clear = _clear_input(input_call)
    
    request = _request_keys(keys, input_call_clear)
    print(request)
    
    call_values = [request [r] for r in keys]
    
    if print_dict == True:
        print(call_values)
    return call_values