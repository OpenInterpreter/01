DEVICE=$(uname -n)
if [[ "$DEVICE" == "rpi" ]]; then
    python -m 01OS.clients.rpi.device
else
    python -m 01OS.clients.macos.device
fi
