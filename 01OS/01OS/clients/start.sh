DEVICE=$(uname -n)
if [[ "$DEVICE" == "rpi" ]]; then
    cd 01OS
    python -m 01OS.clients.rpi.device
else
    cd 01OS
    python -m 01OS.clients.macos.device
fi
