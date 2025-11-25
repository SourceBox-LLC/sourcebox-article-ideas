import replicate
from dotenv import load_dotenv

load_dotenv()

TEXT_MODEL_ID = "openai/gpt-5"


def run_text_model(prompt: str) -> str:
    """Run a text generation model with the given prompt."""
    output = replicate.run(
        TEXT_MODEL_ID,
        input={"prompt": prompt},
    )

    if isinstance(output, str):
        return output
    # Some models return a list/iterator of chunks
    return "".join(str(part) for part in output)
