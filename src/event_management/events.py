from enum import Enum


class Event(Enum):
    CONFIG_SAVED = "CONFIG_SAVED"
    MODEL_DOWNLOAD_COMPLETE = "model_download_complete"
