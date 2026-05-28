import os
from app.models import Session


def generate_delphi_txt(session: Session) -> str:
    now = session.updated_at or session.created_at
    fecha = now.strftime("%d/%m/%Y %H:%M:%S")

    lines = []
    lines.append("[SESSION]")
    lines.append(f"ID={session.id}")
    lines.append(f"PROFESOR={session.user_id}")
    lines.append(f"FECHA={fecha}")
    lines.append("[DATA]")

    errores = 0
    for idx, img in enumerate(session.images):
        seq = f"A{idx + 1:03d}"
        status_str = "OK"
        respuesta_str = ""

        if img.status == "FAILED":
            status_str = "ERR_DETECT"
            respuesta_str = ";;;;;"
        elif img.answers:
            answer_list = []
            has_error = False
            for q_key in sorted(img.answers.keys(), key=lambda k: int(k[1:]) if k[1:].isdigit() else 0):
                val = img.answers[q_key]
                if val == "" or val is None:
                    val = ""
                    has_error = True
                answer_list.append(str(val)[0] if str(val) else "")

            while len(answer_list) < 5:
                answer_list.append("")

            respuesta_str = ";".join(answer_list)
            if has_error:
                status_str = "ERR_BLANK"
        else:
            respuesta_str = ";;;;"
            status_str = "ERR_PROCESS"

        if status_str != "OK":
            errores += 1

        line = f"{seq};{respuesta_str};{status_str}" if respuesta_str else f"{seq};;;;;;{status_str}"
        lines.append(f"{seq};{respuesta_str};{status_str}")

    lines.append("[END]")
    lines.append(f"TOTAL={len(session.images)}")
    lines.append(f"ERRORES={errores}")

    txt = "\r\n".join(lines) + "\r\n"
    return txt


def save_txt_to_file(txt_content: str, output_dir: str, session_id: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{session_id}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(txt_content)
    return filepath
