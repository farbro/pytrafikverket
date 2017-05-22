from datetime import datetime
import argparse
import asyncio
import aiohttp
from trafikverket_train import TrafikverketTrain, StationInfo
from trafikverket import Trafikverket

SEARCH_FOR_STATION = "search-for-station"
GET_TRAIN_STOP = "get-train-stop"

async def async_main(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        #parse arguments!
        parser = argparse.ArgumentParser(description="CLI used to get data from trafikverket")
        parser.add_argument("-key", type=str)
        parser.add_argument("-method", choices=(SEARCH_FOR_STATION, GET_TRAIN_STOP))
        parser.add_argument("-station", type=str)
        parser.add_argument("-from-station", type=str)
        parser.add_argument("-to-station", type=str)
        parser.add_argument("-date-time", type=str)

        args = parser.parse_args()

        train_api = TrafikverketTrain(loop, args.key)
        if args.method == SEARCH_FOR_STATION:
            if args.station is None:
                raise ValueError("-station is required")
            stations = await train_api.search_train_stations(args.station)
            for station in stations:
                print(station.name + " " + station.signature)
        elif args.method == GET_TRAIN_STOP:
            from_station = await train_api.get_train_station(args.from_station)
            to_station = await train_api.get_train_station(args.to_station)
            print("from_station_signature: " + from_station.signature)
            print("to_station_signature:   " + to_station.signature)
            time = datetime.strptime(args.date_time, Trafikverket.date_time_format)
            train_stop = await train_api.get_train_stop(from_station, to_station, time)

            print("id: %s, canceled: %s, advertised time: %s, " %
                  (train_stop.id, train_stop.canceled, train_stop.advertised_time_at_location) +
                  "estimated time: %s, time: %s, state: %s" %
                  (train_stop.estimated_time_at_location, train_stop.time_at_location,
                   train_stop.get_state()))


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main(loop))