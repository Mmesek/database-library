try:
    import dotenv

    dotenv.load_dotenv()
except ModuleNotFoundError:
    pass

import os

HOST = os.getenv("HOST", "postgres")
