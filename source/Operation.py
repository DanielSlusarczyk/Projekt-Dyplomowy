from datetime import datetime, timedelta

def split_data(x:datetime):
    year = x.strftime("%Y")
    month = x.strftime("%m")
    day = x.strftime("%d")
    
    return [year, month, day]