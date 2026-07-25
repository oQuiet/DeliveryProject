from uuid import uuid4

from fastapi import Cookie, Response


def create_session_id(response: Response) -> str:
    print("PROCESS")
    session_id = str(uuid4())  # Generate a unique session ID
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True)
    return session_id


def get_session_id(response: Response, session_id: str | None = Cookie(default=None)) -> str:
    return session_id if session_id else create_session_id(response)
