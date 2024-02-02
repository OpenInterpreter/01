last_timestamp = time.time()

while True:
    messages = get_dmesg(after=last_timestamp)
    last_timestamp = time.time()
    
    for message in messages:
        if passes_filter(message)
            send_to_main(to_lmc(message))

    time.sleep(1)