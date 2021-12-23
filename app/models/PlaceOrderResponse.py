from typing import Optional
from pydantic import BaseModel


class PlaceOrderResponse(BaseModel):
    id: int
    clientId: Optional[str]
    market: str
    type: str
    side: str
    price: Optional[float]
    size: float
    status: str
    filledSize: float
    remainingSize: float
    reduceOnly: bool
    liquidation: Optional[str]
    avgFillPrice: Optional[float]
    postOnly: bool
    ioc: bool
    createdAt: str
    future: Optional[str]
