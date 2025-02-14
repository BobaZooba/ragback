import json
from collections import deque
from typing import Any, Deque

import click
import requests

from backend.domain.entities.character import Character
from backend.domain.entities.message import Message
from backend.domain.entities.user import User
from backend.domain.value_objects.chat_actor import ChatActor
from backend.presentation.api.models.chat import ChatRequest, ChatResponse


class ChatClient:
    def __init__(
            self,
            api_url: str,
            user: User,
            character: Character,
            history_size: int = 15,
    ):
        self.api_url = api_url
        self.user = user
        self.character = character
        self.history: Deque[Message] = deque(maxlen=history_size)

    def post_process_response(self, text: str) -> str:
        prefix = f"{self.character.name}:"

        while text.strip().startswith(prefix):
            text = text[len(prefix):].lstrip()

        double_prefix = f"{prefix} {prefix}"
        while double_prefix in text:
            text = text.replace(double_prefix, prefix)

        text = text.strip()

        while not (text[0].isalnum() or text[0] == "*"):
            text = text[1:].strip()

        return text.strip().split("\n")[0]

    def send_message(self, messages: list[Message]) -> str | None:
        chat_request = ChatRequest(
            messages=messages,
            user=self.user,
            character=self.character,
        )

        try:
            response_data = requests.post(
                url=self.api_url,
                data=chat_request.model_dump_json(),
                headers={"Content-Type": "application/json"},
            )
            response_data.raise_for_status()
            response = ChatResponse(**response_data.json())
            if response.search_results:
                search_result_string = "\n".join(
                    [
                        f"\t\t{result.relevance_score:.2f} - {result.content.text}"
                        for result in response.search_results
                    ]
                )
                click.echo(f"\tSearch results:\n{search_result_string}")
            return self.post_process_response(response.generated_text)
        except requests.exceptions.RequestException as exception:
            click.echo(f"Error communicating with API: {str(exception)}", err=True)
            return None

    def get_greeting(self) -> bool:
        response_text = self.send_message([])
        if response_text is None:
            return False

        self.history.append(Message(text=response_text, actor=ChatActor.CHARACTER))
        click.echo(f"{self.character.name}: {response_text}")
        return True

    def process_user_message(self, user_message: str) -> bool:
        self.history.append(Message(text=user_message, actor=ChatActor.USER))

        response_text = self.send_message(list(self.history))
        if not response_text:
            click.echo(f"Response text is {response_text}")
            return False

        self.history.append(Message(text=response_text, actor=ChatActor.CHARACTER))
        click.echo(f"{self.character.name}: {response_text}")
        return True

    def run(self) -> None:
        click.echo(f"Interact with: {self.api_url}")
        click.echo(f'Starting chat with {self.character.name}. Type "bye" to exit.')
        click.echo("-------------------")

        if not self.get_greeting():
            return

        while True:
            user_message = click.prompt("You")
            if user_message.lower() == "bye":
                break

            if not self.process_user_message(user_message):
                break


def load_config(file_path: str) -> dict[Any, Any] | None:
    try:
        with open(file_path, "r") as file_object:
            return json.load(file_object)
    except (FileNotFoundError, json.JSONDecodeError) as exception:
        click.echo(f"Error loading config {file_path}: {str(exception)}", err=True)
        return None


@click.command()
@click.option(
    "--api-host",
    "-host",
    default="http://0.0.0.0",
    help="Chat API URL",
)
@click.option(
    "--api-port",
    "-port",
    default=8000,
    help="Chat API port",
)
@click.option(
    "--api-method",
    "-method",
    default="/api/v1/chat",
    help="Chat API method",
)
@click.option(
    "--history-size",
    "-h",
    default=15,
    help="Number of messages to keep in history",
)
@click.option(
    "--user-config",
    "-u",
    default="./static/user.json",
    type=str,
    help="Path to user JSON config",
)
@click.option(
    "--character-config",
    "-c",
    default="./static/character.json",
    type=str,
    help="Path to character JSON config",
)
def chat(
        api_host: str,
        api_port: int,
        api_method: str,
        history_size: int,
        user_config: str,
        character_config: str,
) -> None:
    user_data = load_config(user_config)
    character_data = load_config(character_config)

    if user_data is None or character_data is None:
        return

    try:
        user = User(**user_data)
        character = Character(**character_data)
    except (TypeError, ValueError) as exception:
        click.echo(f"Error creating entities: {str(exception)}", err=True)
        return

    api_url = f"{api_host}:{api_port}{api_method}"
    client = ChatClient(api_url, user, character, history_size)
    client.run()


if __name__ == "__main__":
    chat()
