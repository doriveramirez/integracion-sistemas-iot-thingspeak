# Tarea de Integración de Sistemas IoT

Este proyecto implementa una aplicación web en Python para gestionar datos de canales de ThingSpeak.

## Documento de entrega

En la raíz del repositorio se incluye el entregable principal en PDF:

- `ENTREGA_INTEGRACION_SISTEMAS_IOT_THINGSPEAK.pdf`

## Requisitos

- Python 3.11 o superior
- Dependencias del fichero `requirements.txt`

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

La aplicación queda disponible en `http://127.0.0.1:5000`.

## Configuración

La copia pública del proyecto usa por defecto el canal público de ejemplo `12397` para evitar exponer claves o
configuración privada del canal original de la tarea.

Puedes cambiar el canal desde la interfaz o editando `demo_config.json`. Si quieres enviar datos, introduce la
`Write API Key` de tu propio canal desde el formulario principal o define la variable de entorno
`THINGSPEAK_WRITE_API_KEY` antes de arrancar la aplicación.

## Contenido del repositorio

- Aplicación Flask para consultar feeds y estados de ThingSpeak
- Plantillas HTML y estilos CSS
- Pruebas unitarias del cliente de ThingSpeak
- Memoria en PDF y HTML con capturas saneadas para una publicación pública

## Pruebas

```bash
python -m unittest discover -s tests -v
```
