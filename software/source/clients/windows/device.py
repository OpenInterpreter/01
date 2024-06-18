from ..base_device import Device

device = Device()


def main(server_url, tts_service):
    device.server_url = server_url
    device.tts_service = tts_service
    device.start()


if __name__ == "__main__":
    main()
