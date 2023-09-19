#!/bin/ash
if [ -z $1 ]
        then ssid=Rezel-Wifi
else
        ssid=$1
fi
if [ -z $2 ]
        then key=motdepasse
else
        key=$2
fi
echo "Setting up Wi-Fi with $ssid $key"
mkdir -p /tmp/bak
mv -f /etc/config/wireless /tmp/bak/
wifi config
rad5G=`uci show wireless | grep 5g | cut -d "." -f 2`
rad2G=`uci show wireless | grep 2g | cut -d "." -f 2`
cat /etc/config/wireless \
    | sed "s/default_$rad5G/main_ac/" | sed "s/$rad5G/radio_ac/" \
    | sed "s/default_$rad2G/main_n/" | sed "s/$rad2G/radio_n/" \
    | sed "s/channel '1'/channel 'auto'/" | sed "s/channel '36'/channel 'auto'/" \
    | sed "s/OpenWrt/$ssid/" | sed "s/none/psk2/" \
    | sed "s/disabled '1'/disabled '0'/" \
    | tee /etc/config/wireless
uci commit
uci set wireless.main_ac.key=$key
uci set wireless.main_n.key=$key
uci commit
wifi reload
