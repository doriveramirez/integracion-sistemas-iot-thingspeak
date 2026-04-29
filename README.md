# Tarea de Integracion de Sistemas IoT

Este proyecto implementa una aplicacion web en Python para gestionar datos de canales de ThingSpeak.

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

La aplicacion queda disponible en `http://127.0.0.1:5000`.

## Configuracion

La copia publica del proyecto usa por defecto el canal publico de ejemplo `12397` para evitar exponer claves o
configuracion privada del canal original de la tarea.

Puedes cambiar el canal desde la interfaz o editando `demo_config.json`. Si quieres enviar datos, introduce la
`Write API Key` de tu propio canal desde el formulario principal o define la variable de entorno
`THINGSPEAK_WRITE_API_KEY` antes de arrancar la aplicacion.

## Contenido del repositorio

- Aplicacion Flask para consultar feeds y estados de ThingSpeak
- Plantillas HTML y estilos CSS
- Pruebas unitarias del cliente de ThingSpeak
- Memoria en PDF y HTML con capturas saneadas para una publicacion publica

## Pruebas

```bash
python -m unittest discover -s tests -v
```
