# batmeter

batmeter lets you log and plot the data of your local laptop's battery.

## Installation
I recommend using python's virtual environments to keep packages locally

```sh
# create venv
python -m venv ve

# activate venv
source ./ve/bin/activate

# install scripts and dependencies into venv
python -m pip install -e .
```


## Usage
In every new shell you have to activate the venv with `source ./ve/bin/activate`
in the install directory of `batmeter`.
Then you can simply call `batmeter -h` to see the help and run the script.

```sh
usage: batmeter [-h] [-l] [-p] [-i INTERVAL] [-b BATTERY [BATTERY ...]] [-d DATABASE]

Log and plot battery measurements of your notebook

optional arguments:
  -h, --help            show this help message and exit
  -l, --log-only        only use logging function; do not plot
  -p, --plot-only       only use potting function without logging
  -i INTERVAL, --interval INTERVAL
                        specify logging interval in seconds
  -b BATTERY [BATTERY ...], --battery BATTERY [BATTERY ...]
                        name[s] of the device[s] that should be locked.
                        It must exist in /sys/class/power_supply/.
  -d DATABASE, --database DATABASE
                        location for logging TinyDB database 
                        (default: './battery_log.json')
```


### Logging first and plotting after the measurement
```sh
batmeter -b BAT0
```

### Logging only
Logging uses the TinyDB database to store the measured
values by default in your current directory under the name
`battery_log.json`. The standard intervall of logging is 5s.
```sh
batmeter -l -b BAT0
```


### Plotting only
```sh
batmeter -p -b BAT0
```
