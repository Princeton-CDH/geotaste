__version__='0.3.5'

try:
    from .geotaste import *
except (ImportError,ModuleNotFoundError) as e:
    pass