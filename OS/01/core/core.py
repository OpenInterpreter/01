while True:

    message = None
    while message is None:
        message = get_from_queue('to_main')

    if message == user_start_message:
        continue

    messages = get_conversation_history()
    messages.append(message)
    save_conversation_history(message)
    
    sentence = ""

    for chunk in interpreter.chat(messages):
        
        if queue_length() > 0:
            save_conversation_history(interpreter.messages)
            break

        send_to_io(chunk)

        sentence += chunk
        if is_full_sentence(sentence):
            audio = tts(sentence)
            sentence = ""
            send_to_io(audio)