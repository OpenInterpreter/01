from ..base_device import Device

device = Device()


def main(server_url, debug):
    device.server_url = server_url
    device.debug = debug
    device.start()


if __name__ == "__main__":
    main()
