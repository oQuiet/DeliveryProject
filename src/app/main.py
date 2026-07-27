from fastapi import FastAPI
import uvicorn

from app.presentation.routers.parcels import parcelsroute

# if __package__ in {None, ""}:
#     sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

app = FastAPI()

app.include_router(parcelsroute)

if __name__ == "__main__":
    uvicorn.run(app)
