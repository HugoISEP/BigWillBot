from pandas import DataFrame
from pydantic import BaseModel


class CryptoInfo(BaseModel):
    symbol: str
    coins: float
    usd_value: float
    data: DataFrame

    class Config:
        arbitrary_types_allowed = True
