#!/bin/sh

. /bin/boardupgrade.sh

board_prepare_upgrade
mtd erase rootfs_data
mtd write /tmp/openwrt.bin firmware
sleep 3
reboot