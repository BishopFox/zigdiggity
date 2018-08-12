#!/bin/bash

git co https://github.com/secdev/scapy.git
cp patch/zigbee.py scapy/scapy/layers/
cd scapy
python setup.py install
cd ..
rm -r scapy
