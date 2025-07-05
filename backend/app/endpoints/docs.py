import asyncio
from pathlib import Path

from fastapi import APIRouter, status, HTTPException

from app.schemas.question import QuizResult
from app.utils.export_results import get_tasks_results_pdf
from fastapi.responses import FileResponse

api_router = APIRouter(
    prefix="/docs/task_results_pdf",
    tags=["Docs"]
)


@api_router.post("", status_code=status.HTTP_201_CREATED)
async def generate_pdf(results: QuizResult) -> str:
    return await asyncio.to_thread(get_tasks_results_pdf, results)


@api_router.get(
    "/{filename}",
    status_code=status.HTTP_201_CREATED,
    response_class=FileResponse
)
async def get_pdf(filename: str) -> FileResponse:
    if not Path(f"documents/{filename}.pdf").exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return FileResponse(
        f"documents/{filename}.pdf",
        filename=filename,
        media_type="application/pdf",
    )


@api_router.delete(
    "/{filename}",
    status_code=status.HTTP_200_OK
)
async def delete_pdf(filename: str) -> None:
    files = [
        file 
        for file in Path("documents").glob(f"{filename}*") 
        if file.suffix.lower() != '.png'
    ]
    for file in files:
        file.unlink()