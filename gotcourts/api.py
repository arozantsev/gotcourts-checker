# standard modules
import asyncio
from datetime import datetime, timedelta

# third party modules
import aiohttp

# some utility functions
def parse_time(input: int) -> dict:
    return {"h": input // 3600, "mm": (input % 3600) // 60, "s": int(input % 60)}


def to_hr_time(input: int, show_seconds: bool = False) -> str:
    dt = parse_time(input)
    output = f"{dt['h']:02d}:{dt['mm']:02d}"
    if show_seconds:
        output += f":{dt['s']:02d}"
    return output


def get_dates(
    weekdays: list = [5, 6], anchor_date=datetime.today(), n_days: int = 14
) -> list:
    result = []
    for it in range(n_days):
        date = anchor_date + timedelta(days=it)
        if date.weekday() in weekdays:
            result.append(f"{date.year}-{date.month:02d}-{date.day:02d}")
    return result


class GotCourtsAPI:
    def __init__(self,):
        pass

    def get_dates_list(self, weekdays: str, n_days: int = 7) -> list:
        weekdays = [
            self.weekdays.index(day.strip().lower()[:3]) for day in weekdays.split(",")
        ]
        return get_dates(weekdays=weekdays, n_days=int(n_days))

    @property
    def club_mapping(self) -> dict:
        return {"mythenquai": 16, "lengg": 19}

    @property
    def weekdays(self) -> list:
        return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    @staticmethod
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

    def prepare_request_url(self, club: str, date: str) -> str:
        if club not in self.club_mapping.keys():
            raise ValueError(f"Unknown club name: {club}")
        return f"https://apps.gotcourts.com/de/api/public/clubs/{self.club_mapping[club]}/reservations?date={date}"

    def get_available_slots(self, json_r: dict) -> dict:
        # get a dictionary of reservations from response
        reservations = json_r["response"]["reservations"]
        # get courts info from the request
        courts = json_r["response"]["club"]["courts"]
        # get courts dict
        courts_dict = {
            c["id"]: {"name": c["label"], "slots": self.get_slots(c)} for c in courts
        }
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

    @staticmethod
    async def fetch(session, url: str) -> dict:
        """Fetch content from URL"""
        async with session.get(url) as response:
            return await response.json()

    async def get_responses_for_dates(self, club: str, dates: list) -> dict:
        """Fetch content for several dates"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch(session, self.prepare_request_url(club, date))
                for date in dates
            ]
            return await asyncio.gather(*tasks)

    def get_api_response(self, club: str, dates: list) -> str:
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

        responses = loop.run_until_complete(self.get_responses_for_dates(club, dates))
        # make sure number of responses match
        assert len(dates) == len(responses)
        # prepare resulting dictionary
        result_text = ""
        for date, r in zip(dates, responses):
            result_text += f"*{date}* ({club})\n"
            available_slots = self.get_available_slots(r)
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
