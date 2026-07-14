import os
import datetime
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
                elif val == "ERROR" or len(str(val)) > 1:
                    val = "ERROR"
                    has_error = True
                answer_list.append(str(val) if str(val) else "")

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

        lines.append(f"{seq};{respuesta_str}")

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


def generate_qccapdat_txt(session: Session) -> str:
    now = session.updated_at or session.created_at
    lines = []

    for img in session.images:
        a = img.answers or {}
        cols = []

        # 0-59: Q1..Q60
        for i in range(1, 61):
            key = f"Q{i}"
            v = a.get(key, "")
            if v == "" or v is None:
                cols.append("O")
            elif v == "ERROR":
                cols.append("ERROR")
            else:
                cols.append(str(v))

        # 60: RUT XX.XXX.XXX-Y
        rut_digits = []
        for d in range(1, 10):
            v = a.get(f"CEDULA_D{d}", "")
            if v == "ERROR" or v == "" or v is None:
                rut_digits.append(" ")
            else:
                rut_digits.append(str(v))
        rut = f"{''.join(rut_digits[:2])}.{''.join(rut_digits[2:5])}.{''.join(rut_digits[5:8])}-{rut_digits[8]}"
        cols.append(rut)

        # 61: SUBSECTOR = SUBS01 + SUBS02
        s01 = a.get("SUBS01", "")
        s02 = a.get("SUBS02", "")
        if s01 == "ERROR" or s01 == "" or s01 is None:
            s01 = ""
        if s02 == "ERROR" or s02 == "" or s02 is None:
            s02 = ""
        subs = f"{s01}{s02}"
        cols.append(subs if subs else "Omitida")

        # 62: LICEO (default 1)
        cols.append("1")

        # 63: NIVEL-CURSO-LETRA
        nivel = ""
        for nk in ["NIVEL_P", "NIVEL_K", "NIVEL_B", "NIVEL_M"]:
            v = a.get(nk, "")
            if v != "" and v != "ERROR" and v is not None:
                nivel = v
                break
        curso = a.get("CURSO", "")
        if curso == "ERROR" or curso is None:
            curso = ""
        l1 = a.get("LETRA_1", "")
        l2 = a.get("LETRA_2", "")
        if l1 == "ERROR" or l1 is None:
            l1 = ""
        if l2 == "ERROR" or l2 is None:
            l2 = ""
        letra = f"{l1}{l2}"
        cols.append(f"{nivel}-{curso}{letra}" if nivel else "Omitida")

        # 64: FORMA
        forma = a.get("FORMA", "")
        if forma == "ERROR" or forma == "" or forma is None:
            cols.append("Omitida")
        else:
            cols.append(forma)

        # 65: FECHA año_procesado-MES-DIA
        anio = now.strftime("%Y")
        m1 = a.get("MES_1", "")
        m2 = a.get("MES_2", "")
        if m2 != "" and m2 != "ERROR" and m2 is not None:
            mes = m2.zfill(2)
        elif m1 != "" and m1 != "ERROR" and m1 is not None:
            mes = m1.zfill(2)
        else:
            mes = ""
        d1 = a.get("DIA_1", "")
        d2 = a.get("DIA_2", "")
        if d1 == "ERROR" or d1 is None:
            d1 = ""
        if d2 == "ERROR" or d2 is None:
            d2 = ""
        dia = f"{d1}{d2}"
        cols.append(f"{anio}-{mes}-{dia}" if mes and dia else "Omitida")

        # 66: SEXO
        sexo = a.get("SEXO", "")
        if sexo == "ERROR" or sexo == "" or sexo is None:
            cols.append("Omitida")
        else:
            cols.append(sexo)

        lines.append("\t".join(cols))

    return "\r\n".join(lines) + "\r\n"


def save_qccapdat_to_file(txt_content: str, output_dir: str, session_id: str, momento: datetime.datetime = None) -> str:
    os.makedirs(output_dir, exist_ok=True)
    if momento is None:
        momento = datetime.datetime.utcnow()
    filename = f"QcCapdat_{momento.strftime('%Y%m%d_%H%M')}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(txt_content)
    return filepath
