import os
import uuid
import cv2
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import Template, Image as ImageModel, Session
from app.omr_engine.processor import OMRProcessor
from app.omr_engine.evaluation import EvaluationEngine
from app.omr_engine.logger import logger


async def process_single_image_sync(
    db: AsyncSession,
    session_id: uuid.UUID,
    filename: str,
    image_path: str,
    template_id: uuid.UUID,
) -> dict:
    result = await db.execute(select(Template).where(Template.id == template_id))
    template_record = result.scalar_one_or_none()
    if not template_record:
        return {"status": "error", "error_message": f"Template {template_id} not found"}

    template_data = dict(template_record.template_data)
    config_override = dict(template_record.config) if template_record.config else None

    processor = OMRProcessor(template_data, config_override)

    if template_record.marker_image_path:
        marker_path = template_record.marker_image_path
        if os.path.exists(marker_path):
            marker_img = cv2.imread(marker_path, cv2.IMREAD_GRAYSCALE)
            if marker_img is not None:
                for pp in processor.template.pre_processors:
                    if hasattr(pp, 'set_marker_image'):
                        pp.set_marker_image(marker_img)

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"status": "error", "error_message": f"Could not read image: {filename}"}

    result_data = processor.process(img, filename)
    if result_data is None:
        return {
            "status": "error",
            "error_message": "No se detectaron las marcas de esquina. Por favor, reencuadre la foto y asegúrese de que se visualicen los 4 extremos de la cartilla.",
        }

    response_dict, _final_marked_img, _multi_marked = result_data

    score = None
    verdicts = None
    total_q = 0

    if template_record.evaluation_data:
        eval_data = dict(template_record.evaluation_data)
        evaluator = EvaluationEngine(eval_data)
        score, verdicts = evaluator.evaluate(response_dict)
        total_q = len(verdicts) if verdicts else 0

    answers = {}
    for k in sorted(response_dict.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        answers[k] = response_dict.get(k, "")

    return {
        "status": "success",
        "answers": answers,
        "score": score,
        "total": total_q,
        "verdicts": verdicts,
    }
