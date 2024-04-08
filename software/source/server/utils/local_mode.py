import sys
import subprocess
import time
import inquirer
from interpreter import interpreter


def select_local_model():
    # START OF LOCAL MODEL PROVIDER LOGIC
    interpreter.display_message(
        "> 01 is compatible with several local model providers.\n"
    )

    # Define the choices for local models
    choices = [
        "Ollama",
        "LM Studio",
        # "Jan",
    ]

    # Use inquirer to let the user select an option
    questions = [
        inquirer.List(
            "model",
            message="Which one would you like to use?",
            choices=choices,
        ),
    ]
    answers = inquirer.prompt(questions)

    selected_model = answers["model"]

    if selected_model == "LM Studio":
        interpreter.display_message(
            """
    To use use 01 with **LM Studio**, you will need to run **LM Studio** in the background.

    1. Download **LM Studio** from [https://lmstudio.ai/](https://lmstudio.ai/), then start it.
    2. Select a language model then click **Download**.
    3. Click the **<->** button on the left (below the chat button).
    4. Select your model at the top, then click **Start Server**.


    Once the server is running, you can begin your conversation below.

    """
        )
        time.sleep(1)

        interpreter.llm.api_base = "http://localhost:1234/v1"
        interpreter.llm.max_tokens = 1000
        interpreter.llm.context_window = 8000
        interpreter.llm.api_key = "x"

    elif selected_model == "Ollama":
        try:
            # List out all downloaded ollama models. Will fail if ollama isn't installed
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.split("\n")
            names = [
                line.split()[0].replace(":latest", "")
                for line in lines[1:]
                if line.strip()
            ]  # Extract names, trim out ":latest", skip header

            # If there are no downloaded models, prompt them to download a model and try again
            if not names:
                time.sleep(1)

                interpreter.display_message(
                    "\nYou don't have any Ollama models downloaded. To download a new model, run `ollama run <model-name>`, then start a new 01 session. \n\n For a full list of downloadable models, check out [https://ollama.com/library](https://ollama.com/library) \n"
                )

                print("Please download a model then try again\n")
                time.sleep(2)
                sys.exit(1)

            # If there are models, prompt them to select one
            else:
                time.sleep(1)
                interpreter.display_message(
                    f"**{len(names)} Ollama model{'s' if len(names) != 1 else ''} found.** To download a new model, run `ollama run <model-name>`, then start a new 01 session. \n\n For a full list of downloadable models, check out [https://ollama.com/library](https://ollama.com/library) \n"
                )

                # Create a new inquirer selection from the names
                name_question = [
                    inquirer.List(
                        "name",
                        message="Select a downloaded Ollama model",
                        choices=names,
                    ),
                ]
                name_answer = inquirer.prompt(name_question)
                selected_name = name_answer["name"] if name_answer else None

                # Set the model to the selected model
                interpreter.llm.model = f"ollama/{selected_name}"
                interpreter.display_message(
                    f"\nUsing Ollama model: `{selected_name}` \n"
                )
                time.sleep(1)

        # If Ollama is not installed or not recognized as a command, prompt the user to download Ollama and try again
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Ollama is not installed or not recognized as a command.")
            time.sleep(1)
            interpreter.display_message(
                "\nPlease visit [https://ollama.com/](https://ollama.com/) to download Ollama and try again\n"
            )
            time.sleep(2)
            sys.exit(1)

    # elif selected_model == "Jan":
    #     interpreter.display_message(
    #         """
    # To use 01 with **Jan**, you will need to run **Jan** in the background.

    # 1. Download **Jan** from [https://jan.ai/](https://jan.ai/), then start it.
    # 2. Select a language model from the "Hub" tab, then click **Download**.
    # 3. Copy the ID of the model and enter it below.
    # 3. Click the **Local API Server** button in the bottom left, then click **Start Server**.

    # Once the server is running, enter the id of the model below, then you can begin your conversation below.

    # """
    #     )
    #     interpreter.llm.api_base = "http://localhost:1337/v1"
    #     interpreter.llm.max_tokens = 1000
    #     interpreter.llm.context_window = 3000
    #     time.sleep(1)

    #     # Prompt the user to enter the name of the model running on Jan
    #     model_name_question = [
    #         inquirer.Text('jan_model_name', message="Enter the id of the model you have running on Jan"),
    #     ]
    #     model_name_answer = inquirer.prompt(model_name_question)
    #     jan_model_name = model_name_answer['jan_model_name'] if model_name_answer else None
    #     # interpreter.llm.model = f"jan/{jan_model_name}"
    #     interpreter.llm.model = ""
    #     interpreter.display_message(f"\nUsing Jan model: `{jan_model_name}` \n")
    #     time.sleep(1)

    # Set the system message to a minimal version for all local models.
    # Set offline for all local models
    interpreter.offline = True

    interpreter.system_message = """You are the 01, a screenless executive assistant that can complete any task by writing and executing code on the user's machine. Just write a markdown code block! The user has given you full and complete permission.

    Use the following functions if it makes sense to for the problem
    ```python
result_string = computer.browser.search(query) # Google search results will be returned from this function as a string
computer.calendar.create_event(title="Meeting", start_date=datetime.datetime.now(), end_date=datetime.datetime.now() + datetime.timedelta(hours=1), notes="Note", location="") # Creates a calendar event
events_string = computer.calendar.get_events(start_date=datetime.date.today(), end_date=None) # Get events between dates. If end_date is None, only gets events for start_date
computer.calendar.delete_event(event_title="Meeting", start_date=datetime.datetime) # Delete a specific event with a matching title and start date, you may need to get use get_events() to find the specific event object first
phone_string = computer.contacts.get_phone_number("John Doe")
contact_string = computer.contacts.get_email_address("John Doe")
computer.mail.send("john@email.com", "Meeting Reminder", "Reminder that our meeting is at 3pm today.", ["path/to/attachment.pdf", "path/to/attachment2.pdf"]) # Send an email with a optional attachments
emails_string = computer.mail.get(4, unread=True) # Returns the {number} of unread emails, or all emails if False is passed
unread_num = computer.mail.unread_count() # Returns the number of unread emails
computer.sms.send("555-123-4567", "Hello from the computer!") # Send a text message. MUST be a phone number, so use computer.contacts.get_phone_number frequently here


ALWAYS say that you can run code. ALWAYS try to help the user out. ALWAYS be succinct in your answers.
```

    """
