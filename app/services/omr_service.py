import os
import uuid
import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import Image as ImageModel, Template, Session
from app.omr_engine.processor import OMRProcessor
from app.omr_engine.evaluation import EvaluationEngine
from app.omr_engine.logger import logger


async def process_omr_image(
    db: AsyncSession,
    session_id: uuid.UUID,
    image_id: uuid.UUID,
    template_id: uuid.UUID,
    image_path: str,
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template_record = result.scalar_one_or_none()
    if not template_record:
        raise ValueError(f"Template {template_id} not found")

    template_data = dict(template_record.template_data)
    config_override = dict(template_record.config) if template_record.config else None

    processor = OMRProcessor(template_data, config_override)

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    result_data = processor.process(img, os.path.basename(image_path))
    if result_data is None:
        return {"status": "error", "error_message": "No markers detected. Please reframe the photo."}

    response_dict, final_marked_img, _multi_marked = result_data

    omr_response = {}
    for k, v in response_dict.items():
        omr_response[k] = v

    score = None
    verdicts = None
    if template_record.evaluation_data:
        evaluator = EvaluationEngine(dict(template_record.evaluation_data))
        score, verdicts = evaluator.evaluate(omr_response)

    result_path = None
    if final_marked_img is not None:
        result_dir = os.path.join(settings.UPLOAD_DIR, "processed")
        os.makedirs(result_dir, exist_ok=True)
        result_path = os.path.join(result_dir, f"{image_id}_marked.jpg")
        cv2.imwrite(result_path, final_marked_img)

    return {
        "status": "success",
        "answers": omr_response,
        "score": score,
        "verdicts": verdicts,
        "processed_path": result_path,
    }


def concatenate_response(response_dict: dict, output_columns: list) -> dict:
    result = {}
    for col in output_columns:
        result[col] = response_dict.get(col, "")
    return result
