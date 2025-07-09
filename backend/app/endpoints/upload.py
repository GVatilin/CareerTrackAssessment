import io
from app.database.models.question import AIQuestion, Question
from fastapi import APIRouter, Path,Security, UploadFile, File, HTTPException, Depends, status
from app.config import get_settings, DefaultSettings 
from app.utils.s3_manager import S3Client 
from typing import Annotated, List
from app.utils.user import get_current_user
from app.database.connection import get_session
from app.database.models import User
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID 

def get_s3_client(settings: DefaultSettings = Depends(get_settings)) -> S3Client:
    return settings.s3_client

api_router = APIRouter(
    prefix="/file",
    tags=["file"]
)

@api_router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(...),
    s3_client: S3Client = Depends(get_s3_client),
    user: User = Security(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        file_data = await file.read()
        key = f"uploads/{user.id}/{file.filename}"
        await s3_client.upload_file(key, file_data)
        return {"message": "Файл успешно загружен", "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/test/s3")
async def test_s3_connection(s3_client: S3Client = Depends(get_s3_client)):
    try:
        objects = await s3_client.list_objects()
        return {"objects": objects}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка подключения к S3: {e}"
        )

@api_router.get("/get", response_class=StreamingResponse)
async def get_avatar(
    s3_client: S3Client = Depends(get_s3_client),
    user: User = Security(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    key = f"uploads/{user.id}/avatar.jpg"
    try:
        file_data = await s3_client.get_file(key)
        return StreamingResponse(iter([file_data]), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")



@api_router.post("/questions/{question_id}/upload", status_code=status.HTTP_200_OK)
async def upload_question_file(
    question_id: UUID,
    file: UploadFile = File(...),
    s3_client: S3Client = Depends(get_s3_client),
    user: User = Security(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()

    if question is None:
        result = await session.execute(select(AIQuestion).where(AIQuestion.id == question_id))
        question = result.scalar_one_or_none()

    if question is None:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    if question.author_id != user.id:
        raise HTTPException(status_code=403, detail="Нет прав на загрузку файла для этого вопроса")
    file_data = await file.read()
    key = f"uploads/{user.id}/{question_id}/{file.filename}"
    await s3_client.upload_file(key, file_data)
    question.picture = key
    await session.commit()
    await session.refresh(question)

    return {
        "message": "Файл успешно загружен",
        "key": key,
        "question_id": str(question_id),
    }
@api_router.get(
    "/questions/{question_id}/picture",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_question_picture(
    question_id: UUID,
    s3_client: S3Client = Depends(get_s3_client),
    user: User = Security(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question is None:
        result = await session.execute(
            select(AIQuestion).where(AIQuestion.id == question_id)
        )
        question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    if not question.picture:
        raise HTTPException(status_code=404, detail="Файл для этого вопроса не найден")
    try:
        file_bytes = await s3_client.get_file(question.picture)
    except Exception:
        raise HTTPException(status_code=404, detail="Файл не найден в S3")
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{question.picture.split("/")[-1]}"'
        },
    )


