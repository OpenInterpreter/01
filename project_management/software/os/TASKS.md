- [ ] Modify bootloader.
- [ ] Decide: better queue?
      <br>
      So, Michael suggested we simply watch and filter the `dmesg` stream (I think that's what it's called?), so I suppose we could have a script like `/01/core/kernel_watch.py` that puts things into the queue? Honestly knowing we could get it all from one place like that— maybe this should be simpler. **Is the queue folder necessary?** How about we just expect the computer to send {"role": "computer"} messages to a POST endpoint at "/queue" or maybe "/inturrupt" or maybe "/" but with POST? When it gets those it puts them in the redis queue, which is checked frequently, so it's handled immediatly. So then yeah, maybe we do have redis there, then instead of looking at that folder, we check the redis queue. Is this better for any reason? Making the way computer messages are sent = an HTTP request, not putting a file in a folder?
- [ ] Virtualization?
- [ ] Best workflow for pressing to an ISO? Cubic?
- [ ] Putting sensors around the OS to put things into the queue / `dmesg` implementation.
- [ ] Networked input into the queue? (Exploring this makes me thing the "/queue" or something endpoint is smarter to do than the "queue" folder)

# For later

- [ ] We could have `/i` which other interpreter's hit. That behaves more like the OpenAI POST endpoint with stream=True by default (i think this is important for users to see the exchange happening in real time, streaming `event/stream` or whatever). You could imagine some kind of handshake — another interpreter → my interpreter's /i → the sender is unrecognized → computer message is sent to /, prompting AI to ask the user to have the sending interpreter send a specific code → the user tells the sending interpreter to use that specific code → the sender is recognized and added to friends-list (`computer.inetwork.friends()`) → now they can hit eachother's i endpoints freely with `computer.inetwork.friend(id).message("hey")`.
- [ ] (OS team: this will require coordination with the OI core team, so let's talk about it / I'll explain at the next meetup.) When transfering skills that require OS control, the sender can replace those skills with that command, with one input "natural language query" (?) proceeded by the skill function name or something like that. Basically so if you ask it to do something you set up as a skill, it actually asks your computer to do it. If you ask your computer to do it directly, it's more direct.
