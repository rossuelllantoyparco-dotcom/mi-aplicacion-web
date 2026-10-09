# API DataExpert en Docker

Esta API expone el pipeline final de Regresión Logística entrenado en `Trabajo_Final_IA_DataExpert.ipynb`.

El contenedor usa Gunicorn para servir la API de forma adecuada para un despliegue y acepta el puerto `PORT` que asigne la nube.

## Levantar el contenedor

Desde esta carpeta:

```bash
docker compose up -d --build
```

Comprobar el estado:

```bash
curl http://localhost:5000/health
```

## Probar una predicción

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "edad": 35,
    "ingreso_mensual": 3200,
    "antiguedad_meses": 24,
    "consultas_soporte": 3,
    "gasto_mensual": 180,
    "tipo_plan": "Estandar",
    "region": "Costa"
  }'
```

Detenerlo:

```bash
docker compose down
```

## Probar con Postman

Importa el archivo `DataExpert_Docker.postman_collection.json` en Postman.
La colección incluye:

- `GET /health` para verificar que el contenedor está activo.
- `POST /predict` con un ejemplo completo de entrada.

La variable `base_url` ya está configurada como `http://localhost:5000`.

## Pantalla visual

Abre `http://localhost:5000/` para ver el dashboard de bienestar. La pantalla visual calcula un score orientativo de 0 a 300 a partir de horas de sueño, minutos de actividad y nivel de estrés.

El perfil y el último registro del usuario se guardan en el navegador mediante `localStorage`, por lo que el dashboard conserva sus datos al recargar. Esta primera versión es para un usuario en un navegador; para varios usuarios se debe añadir autenticación y una base de datos.

## Endpoints

- `GET /health`: confirma que la API y el modelo están disponibles.
- `POST /predict`: devuelve la predicción, la etiqueta y ambas probabilidades.
## Despliegue en Render

El proyecto incluye `render.yaml` y puede desplegarse como un Web Service Docker.

1. Sube esta carpeta a un repositorio de GitHub.
2. En Render selecciona **New +** y luego **Blueprint**.
3. Conecta el repositorio y confirma el servicio `bienestar-api`.
4. Render construira el Dockerfile y usara `/health` para comprobar el servicio.

Cuando termine, la web quedara disponible en la URL `https://bienestar-api.onrender.com` o en el dominio que Render asigne. La API se usara con `POST /api/wellness`.
