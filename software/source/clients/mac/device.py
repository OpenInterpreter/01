from ..base_device import Device

device = Device()


def main(server_url, debug, play_audio):
    device.server_url = server_url
    device.debug = debug
    device.play_audio = play_audio
    device.start()


if __name__ == "__main__":
    main()
