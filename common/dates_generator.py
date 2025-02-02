from datetime import datetime, timedelta


async def generate_dates():
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime('%m.%d') for i in range(12)][1:]
    return dates
