import logging
from pathlib import Path


def configurar_logger():

    Path("reports").mkdir(
        parents=True,
        exist_ok=True
    )

    logging.basicConfig(

        level=logging.INFO,

        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),

        handlers=[

            logging.FileHandler(
                "reports/ejecucion.log",
                encoding="utf-8"
            ),

            logging.StreamHandler()
        ],

        force=True
    )

    return logging.getLogger("QA")