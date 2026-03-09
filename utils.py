import datetime

def get_dates():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    
    return start_date, end_date