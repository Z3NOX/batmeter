#!/usr/bin/env python3

import argparse
import sys
import signal
from datetime import datetime
from time import time,sleep

from tinydb import TinyDB, Query

from matplotlib import pyplot as plt


p = argparse.ArgumentParser(description="Log and plot battery measurements of your notebook")
p.add_argument("-l", "--log-only", action="store_true", dest="onlylog",
               help="only use logging function; do not plot")
p.add_argument("-p", "--plot-only", action="store_true", dest="onlyplot",
               help="only use potting function without logging")
p.add_argument("-i", "--interval", type=int, default=5,
               help="specify logging interval in seconds")
p.add_argument("-b", "--battery", nargs="+", default=["BAT0"],
               help=("name[s] of the device[s] that should be locked.\n" +
                     "It must exist in /sys/class/power_supply/."))
p.add_argument("-d", "--database", type=str, default="./battery_log.json",
               help=("location for logging TinyDB database \n" +
                     "(default: './battery_log.json')"))
args = p.parse_args()

class GracefulKiller:
    """ Gracefully handle SIGINT and SIGTERM to react on them."""
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

def read_bat_state(bat_name):
    """ Read the battery state of the battery
        named `bat_name` """

    uevent = {}
    with open("/sys/class/power_supply/{}/uevent".format(bat_name)) as file:
        for data in file.readlines():
            data = data.replace('\n', "")
            data = data.replace("POWER_SUPPLY_", "")
            uevent_key = data.split("=")[0]
            uevent_value = data.split("=")[1]

            uevent[uevent_key] = uevent_value

    # enrich data with time
    uevent["DATETIME"] = str(time())
    return uevent


def log_bat_state(db, bat_list, end_cb=lambda _:False,
                  skip_cb=lambda _:False, timediff=5):
    """ reads battery state for each battery in `bat_list`.
        Store measurement to database `db` and waits for
        `timediff` seconds. End of log is determined with
        callback function `end_cb` which gets the uevent.
        You can also define to skip storage of a measurement
        by using the `skip_cb` function.
    """
    counter = 0
    print("Logging ... (interrupt with Ctrl+C)")
    
    # First uevent to check callback initially
    uevent = read_bat_state(bat_list[0])

    # Initialyze class for handle SIGTERM
    killer = GracefulKiller()

    while (not end_cb(uevent)) and (not killer.kill_now):
        try:
            for bat_name in bat_list:
                uevent = read_bat_state(bat_name)
                if not skip_cb(uevent):
                    db.insert(uevent)
                    counter += 1
            sleep(timediff)
            print("Last measurement: {}".format(datetime.now()), end='\r')
        except KeyboardInterrupt:
            break
    print("\n... until now. ({} datapoints taken)".format(counter))


def get_uniq_batID(uevent_it):
    """ uevent iterator that extracts battery IDs"""
    uniq = set()
    for event in uevent_it:
        uniq.add("{}-{}-{}-{}".format(
            event["NAME"],
            event["MANUFACTURER"],
            event["MODEL_NAME"],
            event["SERIAL_NUMBER"]))
    return list(uniq)

def get_uevents_by_batID(db, batID):
    bat = Query()
    name, manu, model, serial = batID.split("-")

    res = db.search(
            (bat.NAME == name) & 
            (bat.MANUFACTURER == manu) & 
            (bat.MODEL_NAME == model) & 
            (bat.SERIAL_NUMBER == serial)
            )
    return res

def show_uevents_by_time(ax, uevent_list, c="b"):
    t = [datetime.fromtimestamp(float(x["DATETIME"])) for x in uevent_list]
    E = [int(x["ENERGY_NOW"])/10**6 for x in uevent_list]  # in Wh
    P = [int(x["POWER_NOW"])/10**6 for x in uevent_list]   # in W
    V = [int(x["VOLTAGE_NOW"])/10**6 for x in uevent_list] # in V

    ax.plot(t, E, c=c, marker="x", ls="solid", label="E(t)/Wh")
    ax.plot(t, P, c=c, marker="x", ls="dashed", label="P(t)/W")
    ax.plot(t, V, c=c, marker="x", ls="dotted", label="U(t)/V")


def skip_power_zero(uevent):
    """ usable as callback function to log_bat_state """
    if uevent["POWER_NOW"] == "0":
        return True
    else:
        return False

def main():

    if args.onlyplot:
        access_mode = "r"    # reading only
    else:
        access_mode = "r+"   # reading and writing

    db = TinyDB(args.database, access_mode=access_mode)

    if not args.onlyplot:
        log_bat_state(db, args.battery, timediff=args.interval,
                      skip_cb=skip_power_zero)

    if args.onlylog:
        return

    fig, axs = plt.subplots(len(args.battery), 1, constrained_layout=True)
    # for one battery fix that axis is inside a list
    try:
        axs[0]
    except TypeError:
        axs = [axs]

    fig.suptitle("battery measurement tool")

    colors = ["b", "r", "g", "y"]
    
    batIDs = get_uniq_batID(iter(db))

    # filter batIDs that match the argument of battery names
    iter_batIDs = []
    for batID in batIDs:
        for bat in  args.battery:
            if bat in batID:
                iter_batIDs.append(batID)

    for i, batID in enumerate(iter_batIDs):
        meas = get_uevents_by_batID(db, batID)
        show_uevents_by_time(axs[i], meas, colors[i])
        axs[i].set_title("{}".format(batID))
        axs[i].legend(loc='upper right', bbox_to_anchor=(1, 1), shadow=True, ncol=1)
    plt.show()


if __name__ == "__main__":
    main()
