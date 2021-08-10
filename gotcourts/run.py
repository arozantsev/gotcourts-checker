# base modules
import argparse
import os

# local modules
from gotcourts.api import GotCourtsAPI, get_dates
from gotcourts.tbot import GotCourtsWaiterBot, GotCourtsCheckerBotService

bin_path = os.path.dirname(os.path.abspath(__file__))

# CLUB_MAPPING = {"mythenquai": 16, "lengg": 19}
# WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


# initialize API class
API = GotCourtsAPI()

# create type class for the running mode
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


def request_processor(msg: str):
    if msg == "":
        return "empty request"
    else:
        prefix = ""
        args = msg.split(" ")
        club = args[0]
        # check if club is present in the available mappings
        if club not in API.club_mapping.keys():
            return f"Unknown club: '{club}'. Available options are: {API.club_mapping.keys()}"

        if len(args[1:]) == 0:
            dates = API.get_dates_list(weekdays="sat, sun", n_days=7)
            prefix = "Unspecified dates, checking Weekend \n\n"
        else:
            dates = API.get_dates_list(weekdays=", ".join(args[1:]), n_days=7)

        return prefix + API.get_api_response(club, dates)


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
            dates = API.get_dates_list(weekdays=args.weekdays, n_days=int(args.ndays))
        else:
            # get dates
            dates = [d for d in args.date.split(" ") if len(d.strip()) > 0]
        # get responses for dates
        result_text = API.get_api_response(args.club, dates)
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
