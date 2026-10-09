from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "modelo_abandono.joblib"
MODEL = joblib.load(MODEL_PATH)

app = Flask(__name__)

REQUIRED_FIELDS = {
    "edad": (int, float),
    "ingreso_mensual": (int, float),
    "antiguedad_meses": (int, float),
    "consultas_soporte": (int, float),
    "gasto_mensual": (int, float),
    "tipo_plan": (str,),
    "region": (str,),
}


def validate_payload(payload):
    if not isinstance(payload, dict):
        return "El cuerpo debe ser un objeto JSON."

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return f"Faltan campos obligatorios: {', '.join(missing)}."

    for field, expected_types in REQUIRED_FIELDS.items():
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, expected_types):
            expected = "número" if field not in {"tipo_plan", "region"} else "texto"
            return f"El campo '{field}' debe ser un {expected}."

    if payload["edad"] < 18 or payload["edad"] > 75:
        return "'edad' debe estar entre 18 y 75."
    if payload["ingreso_mensual"] < 0 or payload["gasto_mensual"] < 0:
        return "Los importes no pueden ser negativos."
    if payload["antiguedad_meses"] < 0 or payload["consultas_soporte"] < 0:
        return "La antigüedad y las consultas no pueden ser negativas."

    return None


@app.get("/health")
def health():
    return jsonify({"status": "ok", "modelo": MODEL_PATH.name})


@app.get("/")
def dashboard():
    return render_template("index.html")


@app.post("/api/wellness")
def wellness():
    payload = request.get_json(silent=True) or {}
    required = {"sueno_horas", "actividad_minutos", "estres"}
    missing = sorted(required - payload.keys())
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}."}), 400

    try:
        sleep_hours = float(payload["sueno_horas"])
        activity_minutes = float(payload["actividad_minutos"])
        stress = float(payload["estres"])
    except (TypeError, ValueError):
        return jsonify({"error": "Los valores deben ser numéricos."}), 400

    if not (0 <= sleep_hours <= 24 and 0 <= activity_minutes <= 300 and 0 <= stress <= 10):
        return jsonify({"error": "Los valores están fuera de rango."}), 400

    sleep_score = round(min(100, max(0, sleep_hours / 8 * 100)))
    activity_score = round(min(100, max(0, activity_minutes / 60 * 100)))
    mental_score = round(min(100, max(0, (10 - stress) * 10)))
    score = round(min(300, (sleep_score + activity_score + mental_score) / 3 * 3.25))

    recommendations = []
    if sleep_hours < 4:
        recommendations.append({
            "categoria": "Descanso prioritario",
            "detalle": "Hoy prioriza dormir y evita conducir si tienes mucha somnolencia. Si se repite, consulta a un profesional de salud.",
            "icono": "☾",
            "tipo": "sleep",
        })
    elif sleep_hours < 5.5:
        recommendations.append({
            "categoria": "Recupera el sueño poco a poco",
            "detalle": "Intenta acostarte 30 a 60 minutos antes esta noche y mantén una hora de despertar estable.",
            "icono": "☾",
            "tipo": "sleep",
        })
    elif sleep_hours < 7:
        recommendations.append({
            "categoria": "Ajusta tu horario de descanso",
            "detalle": "Prueba sumar 30 minutos de sueño esta noche; es un cambio realista y sostenible.",
            "icono": "☾",
            "tipo": "sleep",
        })
    elif sleep_hours > 10:
        recommendations.append({
            "categoria": "Observa tu descanso",
            "detalle": "Si duermes tantas horas y sigues cansado con frecuencia, conviene comentarlo con un profesional.",
            "icono": "☾",
            "tipo": "sleep",
        })
    else:
        recommendations.append({
            "categoria": "Conserva tu rutina de sueño",
            "detalle": "Mantén horarios parecidos y protege tu última hora del día de pantallas y pendientes.",
            "icono": "☾",
            "tipo": "sleep",
        })

    if activity_minutes == 0:
        recommendations.append({
            "categoria": "Empieza con movimiento suave",
            "detalle": "Haz una caminata de 5 minutos o estiramientos ligeros. La meta es comenzar sin exigirte de más.",
            "icono": "↗",
            "tipo": "activity",
        })
    elif activity_minutes < 20:
        recommendations.append({
            "categoria": "Suma unos minutos de movimiento",
            "detalle": "Camina 10 minutos a un ritmo cómodo, idealmente después de una comida o durante una pausa.",
            "icono": "↗",
            "tipo": "activity",
        })
    elif activity_minutes < 30:
        recommendations.append({
            "categoria": "Acércate a 30 minutos",
            "detalle": "Añade 10 minutos de caminata o movilidad según tu energía de hoy.",
            "icono": "↗",
            "tipo": "activity",
        })
    else:
        recommendations.append({
            "categoria": "Mantén tu movimiento",
            "detalle": "Tu actividad de hoy va bien. Alterna caminar, movilidad y descansos para sostener el hábito.",
            "icono": "↗",
            "tipo": "activity",
        })

    if stress >= 9:
        recommendations.append({
            "categoria": "Baja el ritmo por unos minutos",
            "detalle": "Haz una pausa de 5 minutos: exhala más lento de lo que inhalas y aléjate un momento de la pantalla.",
            "icono": "♡",
            "tipo": "mind",
        })
    elif stress >= 7:
        recommendations.append({
            "categoria": "Regula el estrés",
            "detalle": "Prueba 10 respiraciones lentas o una caminata breve antes de retomar una tarea exigente.",
            "icono": "♡",
            "tipo": "mind",
        })
    elif stress >= 5:
        recommendations.append({
            "categoria": "Haz una pausa breve",
            "detalle": "Reserva 3 minutos para respirar, tomar agua y elegir solo la siguiente tarea importante.",
            "icono": "♡",
            "tipo": "mind",
        })
    else:
        recommendations.append({
            "categoria": "Protege tu equilibrio mental",
            "detalle": "Sigue con pausas cortas y actividades que te ayuden a desconectarte sin sobrecargar tu agenda.",
            "icono": "♡",
            "tipo": "mind",
        })

    return jsonify({
        "score": score,
        "habitos": {
            "sueno": sleep_score,
            "actividad": activity_score,
            "mente": mental_score,
        },
        "recomendaciones": recommendations,
    })


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    error = validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    features = pd.DataFrame([payload])
    prediction = int(MODEL.predict(features)[0])
    probability = float(MODEL.predict_proba(features)[0, 1])

    return jsonify(
        {
            "abandono": prediction,
            "etiqueta": "Abandona" if prediction else "Se queda",
            "probabilidad_abandono": round(probability, 4),
            "probabilidad_permanencia": round(1 - probability, 4),
        }
    )


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Ruta no encontrada."}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
