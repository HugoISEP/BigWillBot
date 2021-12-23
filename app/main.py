from logging.config import dictConfig
from typing import Optional
from fastapi import FastAPI
import logging
from fastapi_utils.tasks import repeat_every

from app.configuration.LogConfiguration import log_configuration
from app.services.BigWill import BigWill

dictConfig(log_configuration)
app = FastAPI(debug=True)


@app.get("/")
def get_status():
    return "alive"


@app.on_event("startup")
@repeat_every(seconds=60*30)
def trade():
    logger = logging.getLogger("MAIN")
    logger.info("Trade processed launched")
    big_will = BigWill()
    big_will.run()