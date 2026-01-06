"""
Download a Whisper model by name using Whisper's load_model.
This function only ensures the model is present in the local cache.
"""

from src.runtime.shared_executor import get_shared_executor


def download_whisper_model(model_name: str) -> None:
    try:
        import whisper

        whisper.load_model(model_name, device="cpu")
    except Exception as exc:
        raise RuntimeError(f"Failed to download Whisper model '{model_name}'") from exc


def download_model_async(model_name: str) -> None:
    return get_shared_executor().submit(download_whisper_model, model_name)
