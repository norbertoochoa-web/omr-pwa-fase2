import asyncio
import json
import uuid
import datetime
from pathlib import Path

from app.database import async_session_factory, init_db
from app.models import User, Template
from app.services.auth_service import hash_password

DATA_DIR = Path(__file__).parent.parent / "data" / "catolico"

def load_json(filename: str) -> dict:
    filepath = DATA_DIR / filename
    with open(filepath) as f:
        return json.load(f)


async def seed():
    await init_db()

    template_data = load_json("template.json")
    evaluation_data = load_json("evaluation.json")
    config_data = load_json("config.json")

    page_w, page_h = template_data["pageDimensions"]
    bubble_w, bubble_h = template_data["bubbleDimensions"]

    async with async_session_factory() as db:
        existing_admin = await db.get(User, uuid.UUID("00000000-0000-0000-0000-000000000001"))
        if not existing_admin:
            admin = User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                email="admin@test.com",
                password_hash=hash_password("password123"),
                full_name="Administrador",
                subscription_status="ACTIVE",
                max_images=100,
                expires=datetime.datetime.utcnow() + datetime.timedelta(days=365),
                is_active=True,
            )
            db.add(admin)

            inactive = User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                email="inactive@test.com",
                password_hash=hash_password("inactive123"),
                full_name="Usuario Inactivo",
                subscription_status="EXPIRED",
                max_images=0,
                expires=datetime.datetime.utcnow() - datetime.timedelta(days=30),
                is_active=False,
            )
            db.add(inactive)
            print("Users seeded: admin@test.com / password123")

        existing_template = await db.get(Template, uuid.UUID("00000000-0000-0000-0000-000000000010"))
        if not existing_template:
            template = Template(
                id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
                name="imax_evaluacion",
                institution_id="catolico",
                description="Plantilla IMAX para evaluación de 60 preguntas tipo MCQ5",
                page_width=page_w,
                page_height=page_h,
                bubble_width=bubble_w,
                bubble_height=bubble_h,
                config=config_data,
                template_data=template_data,
                evaluation_data=evaluation_data,
                marker_image_path="omr_marker.jpg",
            )
            db.add(template)
            print("Template 'imax_evaluacion' seeded from data/catolico/.")

        await db.commit()
        print("Seed completed!")


if __name__ == "__main__":
    asyncio.run(seed())
