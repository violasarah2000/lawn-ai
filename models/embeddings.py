import subprocess
import ast

def embed_texts(text_list, model="nomic-embed-text"):
    embeddings = []

    for text in text_list:
        clean = (text or "").strip()

        if not clean:
            embeddings.append([0.0] * 768)
            continue

        result = subprocess.run(
            ["ollama", "run", model, clean],
            text=True,
            capture_output=True
        )

        raw = result.stdout.strip()
        if not raw:
            raise RuntimeError(
                f"Ollama returned no embedding. STDERR:\n{result.stderr}"
            )

        # ⚡ Parse Python-style list
        embedding = ast.literal_eval(raw)
        embeddings.append(embedding)

    return embeddings
