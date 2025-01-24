import json
from pathlib import Path
from typing import Any
from ._codebook_logger import _codebook_logger

logger = _codebook_logger(__name__)

def _load_from_json(folder: Path, file_name: str) -> Any:
    """
    Load data from a JSON file.

    Args:
        folder (Path): The directory containing the JSON file.
        file_name (str): The name of the JSON file (without the .json extension).

    Returns:
        Any: The data loaded from the JSON file.

    Raises:
        FileNotFoundError: If the specified JSON file does not exist.
        json.JSONDecodeError: If there's an error decoding the JSON file.
    """
    file_path = folder / f"{file_name}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file {file_path}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error loading JSON file {file_path}: {e}")
        raise e