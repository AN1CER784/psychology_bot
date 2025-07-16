from datetime import datetime, timedelta


async def generate_dates():
    """
    Generate next 12 days for appointment

    :return:
    """
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime('%d.%m') for i in range(12)][1:]
    return dates


async def get_dict_from_data(state, message, name_string):
    data = await state.get_data()
    title = data.get(f"{name_string}")
    description = message.text
    data = {"title": title, "description": description}
    return data