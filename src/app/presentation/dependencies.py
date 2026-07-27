from typing import Annotated
from uuid import uuid4

from fastapi import Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.parcel_service import ParcelService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import SQLAlchemyParcelRepository


def create_session_id(response: Response) -> str:
    session_id = str(uuid4())  # Generate a unique session ID
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True)
    return session_id


def get_session_id(response: Response, session_id: str | None = Cookie(default=None)) -> str:
    return session_id if session_id else create_session_id(response)


def get_parcel_service(session: Annotated[AsyncSession, Depends(get_db)]) -> ParcelService:
    repository = SQLAlchemyParcelRepository(session)
    return ParcelService(repository)
