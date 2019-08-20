![ZigDiggity - Logo](images/ZigDiggity-2019-Logo_and_Example-1.jpg)

# ZigDiggity Version 2

Introducing *ZigDiggity*, a ZigBee testing framework created by [Bishop Fox](https://www.bishopfox.com/ "Bishop Fox").

*ZigDiggity* version 2 is a major overhaul of the original package and aims to enable security auditors and developers to run complex interactions with ZigBee networks using a single device. 

See 2019 Black Hat USA & DEF CON 27 links:
* [Black Hat USA 2019 - ARSENAL LAB - ZigBee Hacking: Smarter Home Invasion with ZigDiggity - Aug 7-8, 2019](https://www.blackhat.com/us-19/arsenal/schedule/index.html#arsenal-lab---zigbee-hacking-smarter-home-invasion-with-zigdiggity-17151 "Black Hat USA 2019 - ARSENAL LAB - ZigBee Hacking: Smarter Home Invasion with ZigDiggity - Aug 7-8, 2019")
* https://www.defcon.org/html/defcon-27/dc-27-demolabs.html#ZigDiggity

* [YouTube - Zigbee Hacking: Smarter Home Invasion with ZigDiggity - 56sec DEMO - 20Aug2019](https://www.youtube.com/watch?v=rM495gGRTYQ "YouTube - Zigbee Hacking: Smarter Home Invasion with ZigDiggity - 56sec DEMO - 20Aug2019")

<a href="http://www.youtube.com/watch?feature=player_embedded&v=rM495gGRTYQ
" target="_blank"><img src="http://img.youtube.com/vi/rM495gGRTYQ/0.jpg" 
alt="ZigDiggity 2019 DEMO" width="320" height="180" border="10" /></a>



## Installation

Using a default install of Raspbian, perform the following steps:

* Plug your Raspbee into your Raspberry Pi
* Enable serial using the `sudo raspbi-config` command
  * Select "Advanced Options/Serial"
  * Select *NO* to "Would you like a login shell to be accessible over serial?"
  * Select *YES* to enabling serial
  * Restart the Raspberry Pi
* Install GCFFlasher available [Here](https://www.dresden-elektronik.de/funktechnik/service/download/driver/?L=1)
* Flash the Raspbee's firmware
  * `sudo GCFFlasher -f firmware/zigdiggity_raspbee.bin`
  * `sudo GCFFlasher -r`
* Install the python requirements using `pip3 install -r requirements.txt`
* Patch scapy `sudo cp patch/zigbee.py /usr/local/lib/python3.5/dist-packages/scapy/layers/zigbee.py`
* Install wireshark on the device using `sudo apt-get install wireshark`

### Hardware

The current version of ZigDiggity is solely designed for use with the [Raspbee](https://www.dresden-elektronik.de/funktechnik/solutions/wireless-light-control/raspbee/?L=1)
* https://www.amazon.com/RaspBee-premium-ZigBee-Raspberry-Firmware/dp/B00E6300DO
	* ![](images/RaspBee-image-2.jpg)

## Usage

Currently scripts are available in the root of the repository, they can all be run using Python3:

```python3 listen.py -c 15```

When running with wireshark, root privileges may be required.

### Scripts

* `ack_attack.py` - Performs the acknowledge attack against a given network.
* `beacon.py` - Sends a single beacon and listens for a short time. Intended for finding which networks are near you.
* `find_locks.py` - Examines the network traffic on a channel to determine if device behavior looks like a lock. Displays which devices it thinks are locks.
* `insecure_rejoin.py` - Runs an insecure rejoin attempt on the target network.
* `listen.py` - Listens on a channel piping all output to wireshark for viewing.
* `scan.py` - Moves between channels listening and piping the data to wireshark for viewing.
* `unlock.py` - Attempts to unlock a target lock

## Notes

The patterns used by ZigDiggity version 2 are designed to be as reliable as possible. The tool is still in fairly early stages of development, so expect to see improvements over time.
