import yaml 
from .logger import logger

def load_yaml(path:str):
    try:
        with open(path, "r") as file:
            content = yaml.safe_load(file)
            logger.info(f"Content loaded successfully from: {path}")
    except FileNotFoundError:
        logger.error(f"Could not find file: {path}")
        exit()
    except Exception as e:
        logger.error(f"An error occured while loading file: {str(e)}")
        exit()
        
    return content
