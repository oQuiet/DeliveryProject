from fastapi import Depends, Request
from fastapi.routing import APIRouter

from src.presentation.dependencies import get_session_id
from src.presentation.shemas.models import ParcelRequest

parcelsroute = APIRouter()


@parcelsroute.post("/parcels")
async def register_parcel(parcel: ParcelRequest, session_id: str = Depends(get_session_id)) -> dict:
    return {"session_id": session_id, "parcel": parcel}


@parcelsroute.get("/parcels")
async def get_parcels(request: Request) -> dict:
    return {"session_id": request.cookies.get("session_id")}
