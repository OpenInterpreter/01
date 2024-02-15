class Accumulator:
    def __init__(self):
        self.template = {"role": None, "type": None, "format": None, "content": None} 
        self.message = self.template

    def accumulate(self, chunk):
        #print(str(chunk)[:100])
        if type(chunk) == dict:

            if "format" in chunk and chunk["format"] == "active_line":
                # We don't do anything with these
                return None

            if "start" in chunk:
                self.message = chunk
                self.message.pop("start")
                return None

            if "content" in chunk:

                # Display
                print(chunk['content'], end="", flush=True)

                if any(self.message[key] != chunk[key] for key in self.message if key != "content"):
                    self.message = chunk
                if "content" not in self.message:
                    self.message["content"] = chunk["content"]
                else:
                    self.message["content"] += chunk["content"]
                return None

            if "end" in chunk:
                # We will proceed
                message = self.message
                self.message = self.template
                return message

        if type(chunk) == bytes:
            if "content" not in self.message or type(self.message["content"]) != bytes:
                self.message["content"] = b""
            self.message["content"] += chunk
            return None

        