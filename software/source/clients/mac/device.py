from ..base_device import Device

device = Device()


def main(server_url):
    device.server_url = server_url
    device.start()


if __name__ == "__main__":
    main()
