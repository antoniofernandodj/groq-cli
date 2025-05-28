import os
import json
from time import sleep
from pathlib import Path
from typing import List

import typer
from groq import Groq



HISTORY_FILE = os.path.join(os.getcwd(), ".groq_chat_history.json")
GROQ_KEY_FILE = os.path.join(os.getcwd(), ".groq_key.json")
MAX_HISTORY = 20


def ensure_in_path():
    zshrc = Path.home() / ".zshrc"
    bashrc = Path.home() / ".bashrc"
    current_dir = str(Path(__file__).parent.resolve())

    # Checa se já está no PATH
    existing_path = os.environ.get("PATH", "")
    if current_dir in existing_path.split(":"):
        return  # Já está no PATH, não faz nada

    for file in [zshrc, bashrc]:
        if file.exists():
            with open(file, "r", encoding="utf-8") as f:
                lines = f.read()
                if current_dir in lines:
                    continue

        # Adiciona no .zshrc
        line = f'\n# Adicionado automaticamente pelo groq-cli\nexport PATH="$PATH:{current_dir}"\n'
        with open(zshrc, "a", encoding="utf-8") as f:
            f.write(line)

        print(f"\n[ ✔️ PATH atualizado no ~/.{str(file)} com {current_dir} ]")
        print(f"[ 🔄 Execute 'source ~/.{str(file)}' ou reinicie seu terminal para ativar ]")


app = typer.Typer()


ensure_in_path()


class GroqKeyRepository:
    def __init__(self, KEY_FILE: str):
        self.KEY_FILE = KEY_FILE
        if not os.path.exists(self.KEY_FILE):
            with open(self.KEY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    def get_keys(self) -> dict:
        with open(self.KEY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_key(self, key: str) -> dict:
        with open(self.KEY_FILE, "r", encoding="utf-8") as f:
            content = json.load(f)
            return content.get(key)

    def set_key(self, key: str, value: str):
        keys = self.get_keys()
        keys[key] = value
        with open(self.KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2, ensure_ascii=False)


class HistoryRepository:
    def __init__(self, HISTORY_FILE: str):
        self.HISTORY_FILE = HISTORY_FILE
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def load(self) -> list:
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def write(self, history: list):
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-MAX_HISTORY:], f, indent=2, ensure_ascii=False)

    def append(self, role: str, content: str):
        history = self.load()
        history.append({"role": role, "content": content})
        self.write(history)

    def reset(self):
        self.write([])


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

    history_repository = HistoryRepository(HISTORY_FILE)
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
    client = Groq(api_key=groq_key)
    chat_completion = client.chat.completions.create(
        messages=history + [{"role": "user", "content": " ".join(message_words)}],
        model=model,
        stream=stream,
    )

    if stream:
        response = ""
        for chunk in chat_completion:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                sleep(0.06)
                print(delta.content, end="", flush=True)
                response += delta.content

        print()

    else:
        response = chat_completion.choices[0].message.content
        typer.echo(f"\n{response}")

    history_repository.append(role="user", content=" ".join(message_words))
    history_repository.append(role="assistant", content=response)


if __name__ == "__main__":
    app()
