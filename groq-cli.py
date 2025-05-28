import os
from time import sleep
from typing import List

import typer
from groq import Groq
from groq.types.chat import ChatCompletionChunk, ChatCompletion
from repos import HistoryRepository, GroqKeyRepository
from utils import ensure_in_path


HISTORY_FILE = os.path.join(os.getcwd(), ".groq_chat_history.json")
GROQ_KEY_FILE = os.path.join(os.getcwd(), ".groq_key.json")
MAX_HISTORY = 20


app = typer.Typer()


ensure_in_path()


@app.command()
def chat(
    message_words: List[str] = typer.Argument(..., help="Mensagem para enviar ao modelo."),
    model: str = typer.Option(
        "llama-3.3-70b-versatile",
        help="Modelo a ser utilizado (ex: llama-3-70b-8192, llama-3-8b-8192, llama-3-70b-4k)",
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Limpar o histórico antes de enviar."
    ),
    stream: bool = typer.Option(
        True, "--stream", help="Ativar streaming da resposta."
    ),
):
    """
    Envia uma mensagem ao modelo Groq e retorna a resposta.
    """

    history_repository = HistoryRepository(HISTORY_FILE, MAX_HISTORY)
    groq_key_repository = GroqKeyRepository(GROQ_KEY_FILE)

    groq_key = groq_key_repository.get_key('GROQ_API_KEY')
    if not groq_key:
        key = input("API key não encontrada. Por favor,insira a API key: ")
        groq_key_repository.set_key('GROQ_API_KEY', key)
        groq_key = key

    if reset:
        history_repository.reset()
        typer.echo("[ Histórico resetado ]")

    history = history_repository.load()
    client = Groq(api_key=str(groq_key))
    chat_completion = client.chat.completions.create(
        messages=history + [{"role": "user", "content": " ".join(message_words)}],
        model=model,
        stream=stream,
    )

    response = None
    if stream:
        response = ""
        for chunk in chat_completion:
            if not isinstance(chunk, ChatCompletionChunk):
                continue

            delta = chunk.choices[0].delta
            if delta and delta.content:
                sleep(0.06)
                print(delta.content, end="", flush=True)
                response += delta.content

        print()

    else:
        if not isinstance(chat_completion, ChatCompletion):
            return

        response = chat_completion.choices[0].message.content
        typer.echo(f"\n{response}")

    history_repository.append(role="user", content=" ".join(message_words))
    history_repository.append(role="assistant", content=response)


if __name__ == "__main__":
    app()
