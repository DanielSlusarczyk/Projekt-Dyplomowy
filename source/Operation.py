from datetime import datetime, timedelta
import random

def split_data(x:datetime):
    year = x.strftime("%Y")
    month = x.strftime("%m")
    day = x.strftime("%d")
    
    return [year, month, day]

def random_dates(start_date, end_date, n):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    delta = end_date - start_date

    for _ in range(n):
        random_delta = timedelta(days=random.randint(0, delta.days))
        random_date = start_date + random_delta
        dates.append(random_date)

    dates.sort()
    
    return dates