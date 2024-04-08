import os
from datetime import datetime
from pytimeparse import parse
from crontab import CronTab
from uuid import uuid4
from platformdirs import user_data_dir


def schedule(message="", start=None, interval=None) -> None:
    """
    Schedules a task at a particular time, or at a particular interval
    """
    if start and interval:
        raise ValueError("Cannot specify both start time and interval.")

    if not start and not interval:
        raise ValueError("Either start time or interval must be specified.")

    # Read the temp file to see what the current session is
    session_file_path = os.path.join(user_data_dir("01"), "01-session.txt")

    with open(session_file_path, "r") as session_file:
        file_session_value = session_file.read().strip()

    prefixed_message = "AUTOMATED MESSAGE FROM SCHEDULER: " + message

    # Escape the message and the json, cron is funky with quotes
    escaped_question = prefixed_message.replace('"', '\\"')
    json_data = f'{{\\"text\\": \\"{escaped_question}\\"}}'

    command = f"""bash -c 'if [ "$(cat "{session_file_path}")" == "{file_session_value}" ]; then /usr/bin/curl -X POST -H "Content-Type: application/json" -d "{json_data}" http://localhost:10001/; fi' """

    cron = CronTab(user=True)
    job = cron.new(command=command)
    # Prefix with 01 dev preview so we can delete them all in the future
    job_id = "01-dev-preview-" + str(uuid4())
    job.set_comment(job_id)
    if start:
        try:
            start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid datetime format: {start}.")
        job.setall(start_time)
        print(f"Task scheduled for {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    elif interval:
        seconds = parse(interval)
        if seconds <= 60:
            job.minute.every(1)
            print("Task scheduled every minute")
        elif seconds < 3600:
            minutes = max(int(seconds / 60), 1)
            job.minute.every(minutes)
            print(f"Task scheduled every {minutes} minutes")
        elif seconds < 86400:
            hours = max(int(seconds / 3600), 1)
            job.hour.every(hours)
            print(f"Task scheduled every {hours} hour(s)")
        else:
            days = max(int(seconds / 86400), 1)
            job.day.every(days)
            print(f"Task scheduled every {days} day(s)")

    cron.write()
