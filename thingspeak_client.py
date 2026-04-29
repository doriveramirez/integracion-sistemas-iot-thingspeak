from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


BASE_API_URL = "https://api.thingspeak.com"


class ThingSpeakError(RuntimeError):
    """Raised when ThingSpeak returns an invalid response."""


@dataclass(slots=True)
class ChannelConfig:
    channel_id: int
    read_api_key: str = ""
    write_api_key: str = ""
    results: int = 15


class ThingSpeakClient:
    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def build_feed_url(self, config: ChannelConfig) -> str:
        params = [f"results={config.results}"]
        if config.read_api_key:
            params.append(f"api_key={config.read_api_key}")
        return f"{BASE_API_URL}/channels/{config.channel_id}/feeds.json?{'&'.join(params)}"

    def build_status_url(self, config: ChannelConfig) -> str:
        params = [f"results={config.results}"]
        if config.read_api_key:
            params.append(f"api_key={config.read_api_key}")
        return f"{BASE_API_URL}/channels/{config.channel_id}/status.json?{'&'.join(params)}"

    def build_update_url(self, config: ChannelConfig, payload: dict[str, str]) -> str:
        if not config.write_api_key:
            raise ThingSpeakError("Hace falta una Write API Key para enviar datos al canal.")

        params = [f"api_key={config.write_api_key}"]
        for key, value in payload.items():
            if value:
                params.append(f"{key}={requests.utils.quote(str(value))}")
        return f"{BASE_API_URL}/update?{'&'.join(params)}"

    def read_channel(self, config: ChannelConfig) -> dict[str, Any]:
        response = requests.get(self.build_feed_url(config), timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if "channel" not in data or "feeds" not in data:
            raise ThingSpeakError("La respuesta del canal no tiene el formato esperado.")
        return data

    def read_status(self, config: ChannelConfig) -> dict[str, Any]:
        response = requests.get(self.build_status_url(config), timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if "feeds" not in data:
            raise ThingSpeakError("La respuesta de estados no tiene el formato esperado.")
        return data

    def write_update(self, config: ChannelConfig, payload: dict[str, str]) -> str:
        update_url = self.build_update_url(config, payload)
        response = requests.get(update_url, timeout=self.timeout)
        response.raise_for_status()
        message = response.text.strip()
        if message in {"0", "-1"}:
            raise ThingSpeakError(
                "ThingSpeak rechazó la actualización. Revisa la clave o espera el intervalo mínimo entre envíos."
            )
        return message


def normalize_feeds(channel_data: dict[str, Any]) -> list[dict[str, Any]]:
    feeds: list[dict[str, Any]] = []
    for item in channel_data.get("feeds", []):
        row = {
            "created_at": item.get("created_at", ""),
            "entry_id": item.get("entry_id", ""),
            "status": item.get("status"),
        }
        for index in range(1, 9):
            row[f"field{index}"] = item.get(f"field{index}")
        feeds.append(row)
    return feeds


def extract_field_labels(channel_data: dict[str, Any]) -> list[dict[str, str]]:
    channel = channel_data.get("channel", {})
    labels: list[dict[str, str]] = []
    for index in range(1, 9):
        key = f"field{index}"
        value = channel.get(key)
        if value:
            labels.append({"key": key, "label": value})
    return labels


def chart_payload(feeds: list[dict[str, Any]], labels: list[dict[str, str]]) -> list[dict[str, Any]]:
    charts: list[dict[str, Any]] = []
    timestamps = [feed["created_at"] for feed in feeds]
    for label in labels:
        series: list[float | None] = []
        for feed in feeds:
            value = feed.get(label["key"])
            try:
                series.append(float(value) if value is not None else None)
            except (TypeError, ValueError):
                series.append(None)
        charts.append(
            {
                "field": label["key"],
                "label": label["label"],
                "labels": timestamps,
                "data": series,
            }
        )
    return charts
