from logging.config import dictConfig
from fastapi import FastAPI
import logging
from fastapi_utils.tasks import repeat_every

from app.configuration.LogConfiguration import log_configuration
from app.services.BigWill import BigWill
from app.services.Utils import Utils

dictConfig(log_configuration)
app = FastAPI(debug=True)


@app.get("/status")
def get_status():
    return "alive"


@app.get("/strategy")
def get_status():
    return "BIG_WILL"


@app.get("/markets")
def get_markets():
    return Utils.load_json_pair_symbols()


@app.on_event("startup")
@repeat_every(seconds=60*30)
def trade():
    logger = logging.getLogger("MAIN")
    logger.info("Trade processed launched")
    big_will = BigWill()
    big_will.run()
