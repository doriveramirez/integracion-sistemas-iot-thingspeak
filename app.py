from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, flash, redirect, render_template, request, url_for

from thingspeak_client import (
    ChannelConfig,
    ThingSpeakClient,
    ThingSpeakError,
    chart_payload,
    extract_field_labels,
    normalize_feeds,
)


ROOT = Path(__file__).parent
APP = Flask(__name__)
APP.secret_key = "iot-thingspeak-demo-secret"
CLIENT = ThingSpeakClient()
DISPLAY_FIXES = {
    "Estacion meteorologica David Orive": "Estación meteorológica David Orive",
    "Canal para la gestion de datos ambientales de una estacion IoT.": "Canal para la gestión de datos ambientales de una estación IoT.",
    "Presion": "Presión",
}


def load_demo_config() -> dict[str, Any]:
    return json.loads((ROOT / "demo_config.json").read_text(encoding="utf-8"))


def build_config_from_request() -> ChannelConfig:
    defaults = load_demo_config()
    channel_id = request.values.get("channel_id", str(defaults["channel_id"])).strip()
    read_api_key = request.values.get("read_api_key", defaults["read_api_key"]).strip()
    write_api_key = request.values.get(
        "write_api_key",
        defaults["write_api_key"] or os.getenv("THINGSPEAK_WRITE_API_KEY", ""),
    ).strip()
    results = request.values.get("results", str(defaults["results"])).strip()

    return ChannelConfig(
        channel_id=int(channel_id),
        read_api_key=read_api_key,
        write_api_key=write_api_key,
        results=max(1, min(int(results), 50)),
    )


def build_form_state(config: ChannelConfig) -> dict[str, Any]:
    return {
        "channel_id": config.channel_id,
        "read_api_key": config.read_api_key,
        "write_api_key": config.write_api_key,
        "results": config.results,
    }


def prettify_text(value: str | None) -> str | None:
    if value is None:
        return None
    return DISPLAY_FIXES.get(value, value)


@APP.get("/")
def index() -> str:
    config = build_config_from_request()
    context = load_dashboard_context(config)
    return render_template("index.html", **context)


@APP.post("/send")
def send_data() -> Any:
    try:
        config = build_config_from_request()
        payload = {}
        for index in range(1, 9):
            value = request.form.get(f"field{index}", "").strip()
            if value:
                payload[f"field{index}"] = value

        status = request.form.get("status", "").strip()
        if status:
            payload["status"] = status

        if not payload:
            raise ThingSpeakError("Debes indicar al menos un campo o un estado para enviar datos.")

        entry_id = CLIENT.write_update(config, payload)
        flash(f"Actualización enviada correctamente. ThingSpeak devolvió entry id {entry_id}.", "success")
    except (ThingSpeakError, ValueError) as exc:
        flash(str(exc), "error")

    query = {
        "channel_id": request.form.get("channel_id", ""),
        "read_api_key": request.form.get("read_api_key", ""),
        "write_api_key": request.form.get("write_api_key", ""),
        "results": request.form.get("results", ""),
    }
    return redirect(url_for("index", **query))


def load_dashboard_context(config: ChannelConfig) -> dict[str, Any]:
    try:
        channel_data = CLIENT.read_channel(config)
        status_data = CLIENT.read_status(config)
        channel = dict(channel_data["channel"])
        channel["name"] = prettify_text(channel.get("name"))
        channel["description"] = prettify_text(channel.get("description"))
        for index in range(1, 9):
            key = f"field{index}"
            channel[key] = prettify_text(channel.get(key))
        channel_data = dict(channel_data)
        channel_data["channel"] = channel
        feed_rows = normalize_feeds(channel_data)
        status_rows = normalize_feeds(status_data)
        field_labels = extract_field_labels(channel_data)
        charts = chart_payload(feed_rows, field_labels)
        status_total = len([row for row in status_rows if row.get("created_at")])
        return {
            "config": config,
            "form_state": build_form_state(config),
            "channel": channel,
            "field_labels": field_labels,
            "feed_rows": feed_rows,
            "status_rows": status_rows,
            "charts": charts,
            "status_total": status_total,
            "feed_url": CLIENT.build_feed_url(config),
            "status_url": CLIENT.build_status_url(config),
            "error_message": "",
        }
    except Exception as exc:
        return {
            "config": config,
            "form_state": build_form_state(config),
            "channel": {},
            "field_labels": [],
            "feed_rows": [],
            "status_rows": [],
            "charts": [],
            "status_total": 0,
            "feed_url": CLIENT.build_feed_url(config),
            "status_url": CLIENT.build_status_url(config),
            "error_message": str(exc),
        }


if __name__ == "__main__":
    APP.run(debug=True)
