import re

def _indicator_to_file_name(indicator: str) -> str:
    """
    Converts an indicator name to a valid file name.

    Args:
        indicator (str): The original indicator name.

    Returns:
        str: A valid file name derived from the indicator.

    Example:
        >>> indicator_to_file_name("Ease of doing business score (DB17-20 methodology)")
        'ease_of_doing_business_score_db17_20_methodology'
    """
    # Convert to lowercase
    file_name = indicator.lower()
    
    # Replace spaces and special characters with underscores
    file_name = re.sub(r'[^\w\s-]', '_', file_name)
    
    # Replace consecutive spaces or underscores with a single underscore
    file_name = re.sub(r'[\s_]+', '_', file_name)
    
    # Remove leading/trailing underscores
    file_name = file_name.strip('_')

    return file_name
