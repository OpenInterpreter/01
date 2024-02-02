while True:

    if button.is_pressed():
        send_to_main(user_start_message)
        send_to_websocket(user_start_message)

        audio_chunks = []
        for audio_chunk in listen():
            audio_chunks.append(chunk)
            if not button.is_pressed():
                break

        text = stt(audio_chunks)
        send_to_main(text)
        send_to_websocket(user_end_message)
    
    chunk = get_from_queue('to_io')
    if chunk:
        send_to_websocket(chunk)
        sentence += chunk["content"]
        if is_full_sentence(sentence)
            tts(sentence)
            sentence = []

    message = check_websocket()
    if message:
        send_to_main(message)
