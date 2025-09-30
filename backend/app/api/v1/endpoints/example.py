from fastapi import APIRouter
from app.schemas.example import ExampleResponse

router = APIRouter()

@router.get("/", response_model=ExampleResponse)
async def get_example():
    return ExampleResponse(message="Hello from FastAPI!")
