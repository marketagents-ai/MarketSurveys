import json
from json import JSONDecodeError
from pathlib import Path
from pydantic import BaseModel
from ._codebook_logger import _codebook_logger

logger = _codebook_logger(__name__)

def _save_to_json(self, folder: Path, file_name: str, model: BaseModel) -> None:
    """
    Save a Pydantic model to a JSON file.

    This method saves the given Pydantic model as a JSON file in the specified folder.
    If the file already exists, it will be overwritten.
    Args:
        folder (Path): The directory where the JSON file will be saved.
        file_name (str): The name of the JSON file (without the .json extension).
        model (BaseModel): The Pydantic model to be saved.

    Raises:
        Exception: If there's an error while writing the JSON file.

    Note:
        The method will create the folder if it doesn't exist.
    """
    e = None
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{file_name}.json"
    try:
        with open(file_path, 'w') as f:
            json.dump(model.model_dump(), f, indent=4)
    except IOError as e:
        logger.error(f"I/O error occurred while saving JSON file {file_path}: {e}")
    except JSONDecodeError as e:
        logger.error(f"JSON encoding error occurred while saving file {file_path}: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied while saving JSON file {file_path}: {e}")
    except OSError as e:
        logger.error(f"OS error occurred while saving JSON file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred while saving JSON file {file_path}: {e}")
    finally:
        if e:
            raise e
