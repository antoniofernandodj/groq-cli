from pathlib import Path
import os

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
