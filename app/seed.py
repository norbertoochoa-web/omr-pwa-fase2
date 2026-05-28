import asyncio
import uuid
from passlib.context import CryptContext

from app.database import async_session_factory, init_db
from app.models import User, Template
from app.services.auth_service import hash_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

IMAX_TEMPLATE_DATA = {
    "pageDimensions": [1600, 2300],
    "bubbleDimensions": [43, 43],
    "customLabels": {},
    "fieldBlocks": {
        "C1_G1": {"fieldType": "QTYPE_MCQ5", "origin": [35, 1147], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q1", "Q2", "Q3", "Q4", "Q5"]},
        "C1_G2": {"fieldType": "QTYPE_MCQ5", "origin": [35, 1527], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q6", "Q7", "Q8", "Q9", "Q10"]},
        "C1_G3": {"fieldType": "QTYPE_MCQ5", "origin": [35, 1908], "bubblesGap": 60, "labelsGap": 72, "fieldLabels": ["Q11", "Q12", "Q13", "Q14", "Q15"]},
        "C2_G1": {"fieldType": "QTYPE_MCQ5", "origin": [450, 1147], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q16", "Q17", "Q18", "Q19", "Q20"]},
        "C2_G2": {"fieldType": "QTYPE_MCQ5", "origin": [450, 1527], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q21", "Q22", "Q23", "Q24", "Q25"]},
        "C2_G3": {"fieldType": "QTYPE_MCQ5", "origin": [450, 1908], "bubblesGap": 60, "labelsGap": 72, "fieldLabels": ["Q26", "Q27", "Q28", "Q29", "Q30"]},
        "C3_G1": {"fieldType": "QTYPE_MCQ5", "origin": [925, 1147], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q31", "Q32", "Q33", "Q34", "Q35"]},
        "C3_G2": {"fieldType": "QTYPE_MCQ5", "origin": [925, 1527], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q36", "Q37", "Q38", "Q39", "Q40"]},
        "C3_G3": {"fieldType": "QTYPE_MCQ5", "origin": [925, 1908], "bubblesGap": 60, "labelsGap": 72, "fieldLabels": ["Q41", "Q42", "Q43", "Q44", "Q45"]},
        "C4_G1": {"fieldType": "QTYPE_MCQ5", "origin": [1310, 1147], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q46", "Q47", "Q48", "Q49", "Q50"]},
        "C4_G2": {"fieldType": "QTYPE_MCQ5", "origin": [1310, 1527], "bubblesGap": 60, "labelsGap": 70, "fieldLabels": ["Q51", "Q52", "Q53", "Q54", "Q55"]},
        "C4_G3": {"fieldType": "QTYPE_MCQ5", "origin": [1310, 1908], "bubblesGap": 60, "labelsGap": 72, "fieldLabels": ["Q56", "Q57", "Q58", "Q59", "Q60"]},
    },
    "preProcessors": [
        {"name": "CropOnMarkers", "options": {"relativePath": "omr_marker.jpg", "sheetToMarkerWidthRatio": 17}}
    ],
}

IMAX_EVALUATION_DATA = {
    "source_type": "custom",
    "options": {
        "should_explain_scoring": True,
        "questions_in_order": [f"Q{i}" for i in range(1, 61)],
        "answers_in_order": (
            ["A", "B", "C", "D", "E"] +
            ["A"] * 55
        ),
    },
    "marking_schemes": {
        "DEFAULT": {"correct": 1, "incorrect": 0, "unmarked": 0}
    },
}

IMAX_CONFIG = {
    "dimensions": {
        "display_width": 500,
        "display_height": 850,
        "processing_width": 1350,
        "processing_height": 2300,
    },
    "outputs": {
        "show_image_level": 0,
        "save_image_level": 5,
        "filter_out_multimarked_files": False,
    },
    "alignment_params": {
        "auto_align": True,
    },
}


async def seed():
    await init_db()
    async with async_session_factory() as db:
        existing_user = await db.get(User, uuid.UUID("00000000-0000-0000-0000-000000000001"))
        if not existing_user:
            admin = User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="Administrador",
                subscription_status="ACTIVE",
                is_active=True,
            )
            db.add(admin)

            inactive = User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                username="inactive_user",
                password_hash=hash_password("inactive123"),
                full_name="Usuario Inactivo",
                subscription_status="EXPIRED",
                is_active=False,
            )
            db.add(inactive)
            print("Users seeded.")

        existing_template = await db.get(Template, uuid.UUID("00000000-0000-0000-0000-000000000010"))
        if not existing_template:
            template = Template(
                id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
                name="imax_evaluacion",
                description="Plantilla IMAX para evaluación de 60 preguntas tipo MCQ5",
                page_width=1600,
                page_height=2300,
                bubble_width=43,
                bubble_height=43,
                config=IMAX_CONFIG,
                template_data=IMAX_TEMPLATE_DATA,
                evaluation_data=IMAX_EVALUATION_DATA,
                marker_image_path="omr_marker.jpg",
            )
            db.add(template)
            print("Template 'imax_evaluacion' seeded.")

        await db.commit()
        print("Seed completed!")


if __name__ == "__main__":
    asyncio.run(seed())
