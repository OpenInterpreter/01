import os


class Llm:
    def __init__(self, config):

        interpreter = config["interpreter"]

        # Required environment variables
        """
        export AZURE_API_KEY = 
        export AZURE_API_BASE =
        export AZURE_API_VERSION =
        export AZURE_DEPLOYMENT_ID =
        """

        # Optional : Set environment variables for Azure OpenAI directly here
        """ 
        os.environ["AZURE_API_KEY"] = api_key
        os.environ["AZURE_API_BASE"] = api_base
        os.environ["AZURE_API_VERSION"] = api_version
        os.environ["AZURE_DEPLOYMENT_ID"] = azure_deployment_id
        """

        azure_deployment_id = os.getenv("AZURE_DEPLOYMENT_ID")
        interpreter.llm.model = f"azure/{azure_deployment_id}"

        config.pop("interpreter", None)
        config.pop("service_directory", None)

        for key, value in config.items():
            setattr(interpreter, key.replace("-", "_"), value)

        self.llm = interpreter.llm.completions
