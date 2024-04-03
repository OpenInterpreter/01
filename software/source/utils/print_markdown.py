from rich.console import Console
from rich.markdown import Markdown


def print_markdown(markdown_text):
    console = Console()
    md = Markdown(markdown_text)
    print("")
    console.print(md)
    print("")
