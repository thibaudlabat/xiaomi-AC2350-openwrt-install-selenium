#!/bin/sh
echo "Debut du script flash_firmware.sh"


. /bin/boardupgrade.sh

board_prepare_upgrade
mtd erase rootfs_data
mtd write /tmp/openwrt.bin firmware

echo "Fin du script flash_firmware.sh (suivi de sleep 3 puis de reboot)"
sleep 3
reboot

