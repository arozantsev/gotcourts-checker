# base modules
import argparse
import os
import asyncio
from datetime import datetime, timedelta

# third party modules
import aiohttp

# local modules
from gotcourts.tbot import GotCourtsWaiterBot, GotCourtsCheckerBotService

bin_path = os.path.dirname(os.path.abspath(__file__))

CLUB_MAPPING = {"mythenquai": 16, "lengg": 19}
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


class RunMode:
    single = "single"
    service = "service"


parser = argparse.ArgumentParser()
parser.add_argument(
    "--date",
    type=str,
    default=os.getenv("GOTCOURTS_DATE"),
    help="date for which empty slots should be crawled",
)
parser.add_argument(
    "--weekdays",
    type=str,
    default=os.getenv("GOTCOURTS_WEEKDAYS", "sat,sun"),
    help="days of the week that need to be checked",
)
parser.add_argument(
    "--ndays",
    type=str,
    default=os.getenv("GOTCOURTS_NDAYS", "14"),
    help="number of days in the future to be checked",
)
parser.add_argument(
    "--club",
    type=str,
    default=os.getenv("GOTCOURTS_CLUB", "mythenquai"),
    help="tennis club",
)
parser.add_argument(
    "--ttoken",
    type=str,
    default=os.getenv("TELEGRAM_TOKEN"),
    help="token for telegram bot access",
)
parser.add_argument(
    "--tconf",
    type=str,
    default=os.getenv("TELEGRAM_CONFIG_PATH", f"{bin_path}/../config.yaml"),
    help="token for telegram bot access",
)
parser.add_argument(
    "--mode", type=str, default=RunMode.single, help="code running mode"
)

# utility functions
def parse_time(input: int) -> dict:
    return {"h": input // 3600, "mm": (input % 3600) // 60, "s": int(input % 60)}


def to_hr_time(input: int, show_seconds: bool = False) -> str:
    dt = parse_time(input)
    output = f"{dt['h']:02d}:{dt['mm']:02d}"
    if show_seconds:
        output += f":{dt['s']:02d}"
    return output


def get_slots(input, start_time: int = 13):
    ot = input["openingTime"] // input["interval"]
    ct = input["closingTime"] // input["interval"]

    return set(
        [
            (
                to_hr_time(it * input["interval"]),
                to_hr_time((it + dur) * input["interval"]),
            )
            for dur in input["durations"]
            for it in range(ot, ct, dur)
            if it >= start_time * 60
        ]
    )


def prepare_request_url(club: str, date: str) -> str:
    if club not in CLUB_MAPPING.keys():
        raise ValueError(f"Unknown club name: {club}")
    return f"https://apps.gotcourts.com/de/api/public/clubs/{CLUB_MAPPING[club]}/reservations?date={date}"


def get_available_slots(json_r: dict) -> dict:
    # get a dictionary of reservations from response
    reservations = json_r["response"]["reservations"]
    # get courts info from the request
    courts = json_r["response"]["club"]["courts"]
    # get courts dict
    courts_dict = {c["id"]: {"name": c["label"], "slots": get_slots(c)} for c in courts}
    # remove reservations from available slots
    for res in reservations:
        res_set = set(
            [
                (to_hr_time(it * 60), to_hr_time((it + 60) * 60))
                for it in range(res["startTime"] // 60, res["endTime"] // 60, 60)
            ]
        )
        courts_dict[res["courtId"]]["slots"] -= res_set

    return {
        v["name"]: list(v["slots"])
        for k, v in courts_dict.items()
        if len(v["slots"]) > 0
    }


def get_dates(
    weekdays: list = [5, 6], anchor_date=datetime.today(), n_days: int = 14
) -> list:
    result = []
    for it in range(n_days):
        date = anchor_date + timedelta(days=it)
        if date.weekday() in weekdays:
            result.append(f"{date.year}-{date.month:02d}-{date.day:02d}")
    return result


async def fetch(session, url: str) -> dict:
    """Fetch content from URL"""
    async with session.get(url) as response:
        return await response.json()


async def get_responses_for_dates(club: str, dates: list) -> dict:
    """Fetch content for several dates"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, prepare_request_url(args.club, date)) for date in dates]
        return await asyncio.gather(*tasks)


def get_api_response(club: str, dates: list) -> str:
    """Get the list of available slots for a specific club for a specific list of dates.

    Args:
        club (str): club name
        dates (list): list of dates

    Raises:
        RuntimeError: if event loop cannot be initialized

    Returns:
        str: description of available slots
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = asyncio.new_event_loop()
        else:
            raise RuntimeError(e)

    responses = loop.run_until_complete(get_responses_for_dates(club, dates))
    # make sure number of responses match
    assert len(dates) == len(responses)
    # prepare resulting dictionary
    result_text = ""
    for date, r in zip(dates, responses):
        result_text += f"*{date}* ({club})\n"
        available_slots = get_available_slots(r)
        if len(available_slots) > 0:
            result_text += (
                "\n".join(
                    [
                        f"{k}:  " + ", ".join(sorted([it[0] for it in v]))
                        for k, v in available_slots.items()
                    ]
                )
                + "\n\n"
            )
        else:
            result_text += "-- all reserved\n\n"
    return result_text


def request_processor(msg: str):
    if msg == "":
        return "empty request"
    else:
        prefix = ""
        args = msg.split(" ")
        club = args[0]
        # check if club is present in the available mappings
        if club not in CLUB_MAPPING.keys():
            return (
                f"Unknown club: '{club}'. Available options are: {CLUB_MAPPING.keys()}"
            )

        weekdays = [WEEKDAYS.index(day.strip().lower()[:3]) for day in args[1:]]

        if len(weekdays) == 0:
            weekdays = [
                WEEKDAYS.index(day.strip().lower()[:3]) for day in ["sat", "sun"]
            ]
            prefix = "Unspecified dates, checking Weekend \n\n"

        dates = get_dates(weekdays=weekdays, n_days=7)
        return prefix + get_api_response(club, dates)


def main(args):
    # check code run mode
    if args.mode == RunMode.service:
        assert args.ttoken, "Telegram token is not available"
        service = GotCourtsCheckerBotService(
            args.ttoken, request_processor=request_processor
        )
        service.init_service()
        service.run()

    elif args.mode == RunMode.single:
        if args.date is None:
            weekdays = [
                WEEKDAYS.index(day.strip().lower()[:3])
                for day in args.weekdays.split(",")
            ]
            dates = get_dates(weekdays=weekdays, n_days=int(args.ndays))
        else:
            # get dates
            dates = [d for d in args.date.split(" ") if len(d.strip()) > 0]
        # get responses for dates
        result_text = get_api_response(args.club, dates)
        # Telegram Bot
        if args.ttoken is None:
            print("No Telegram Token is provided -> skipping")
        else:
            # initialize bot
            bot = GotCourtsWaiterBot(args.ttoken, args.tconf)
            # send message
            bot.message_all(result_text)

        # print results
        print(result_text)
        return result_text
    else:
        raise NotImplementedError(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
