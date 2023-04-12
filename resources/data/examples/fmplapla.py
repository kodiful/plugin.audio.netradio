#!/usr/bin/env python3
# coding: utf-8
# vim:fenc=utf-8 ff=unix ft=python ts=4 sw=4 sts=4 si et :

"""
pre-flight:
    pip install requests websocket-client

usage:
    fmplapla --station fmhanabi --time 1800 | ffplay -nodisp -hide_banner -autoexit -i pipe:
    fmplapla --station fmhanabi             | mpv -
    env DEBUG=1 fmplapla -s fmhanabi # debug print

thanks to:
    fmplapla.py - Pastebin.com https://pastebin.com/gQ0Ay2aN
"""

import sys
import time
import argparse
import requests
import websocket


class fmplapla:

    def __init__(self, station_id, duration=0):
        self.station_id = station_id
        self.duration = duration
        self.start_time = time.time()
        # token, location
        url = f'https://api.radimo.smen.biz/api/v1/select_stream?station={self.station_id}&channel=0&quality=high&burst=5'
        res = requests.post(url)
        json = res.json()
        self.token = json['token']
        self.location = json['location']
        self.ws = websocket.WebSocketApp(
            self.location,
            subprotocols=['listener.fmplapla.com'],
            on_open=self._on_open,
            on_message=self._on_message)
        try:
            self.ws.run_forever()
        except (Exception, KeyboardInterrupt, SystemExit) as e:
            self.ws.close()

    def _on_open(self, data):
        self.ws.send(self.token)

    def _on_message(self, data, message):
        if data:
            sys.stdout.buffer.write(message)
        if self.duration > 0:
            if self.duration < (time.time() - self.start_time):
                raise KeyboardInterrupt


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--station', required=True, help='station id')
    parser.add_argument('-d', '--duration', type=int, default=0, help='duration')
    args = parser.parse_args()
    fmplapla(args.station, args.duration)
