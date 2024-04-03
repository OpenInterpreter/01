class Llm:
    def __init__(self, config):
        # Litellm is used by OI by default, so we just modify OI

        interpreter = config["interpreter"]
        config.pop("interpreter", None)
        config.pop("service_directory", None)
        for key, value in config.items():
            setattr(interpreter, key.replace("-", "_"), value)

        self.llm = interpreter.llm.completions
