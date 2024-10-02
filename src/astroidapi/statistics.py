import math
import astroidapi.surrealdb_handler as surrealdb_handler

async def get_statistics():
    statistics = await surrealdb_handler.Statistics.getall()
    total_messages = statistics["messages"]["total"]
    def round_down_to_nearest(x, base):
        return base * math.floor(x / base)

    if total_messages < 10:
        total_messages_rounded = total_messages
    elif total_messages < 50:
        total_messages_rounded = round_down_to_nearest(total_messages, 10)
    elif total_messages < 100:
        total_messages_rounded = round_down_to_nearest(total_messages, 50)
    elif total_messages < 500:
        total_messages_rounded = round_down_to_nearest(total_messages, 100)
    elif total_messages < 1000:
        total_messages_rounded = round_down_to_nearest(total_messages, 500)
    else:
        total_messages_rounded = round_down_to_nearest(total_messages, 1000)
    statistics["messages"]["total_rounded"] = total_messages_rounded

    total_monthly_messages = statistics["messages"]["month"]
    if total_monthly_messages < 10:
        total_monthly_messages_rounded = total_monthly_messages
    elif total_monthly_messages < 50:
        total_monthly_messages_rounded = round_down_to_nearest(total_monthly_messages, 10)
    elif total_monthly_messages < 100:
        total_monthly_messages_rounded = round_down_to_nearest(total_monthly_messages, 50)
    elif total_monthly_messages < 500:
        total_monthly_messages_rounded = round_down_to_nearest(total_monthly_messages, 100)
    elif total_monthly_messages < 1000:
        total_monthly_messages_rounded = round_down_to_nearest(total_monthly_messages, 500)
    else:
        total_monthly_messages_rounded = round_down_to_nearest(total_monthly_messages, 1000)

    statistics["messages"]["month_rounded"] = total_monthly_messages_rounded


    return statistics

async def update_statistics():
    await surrealdb_handler.Statistics.update_messages(1)