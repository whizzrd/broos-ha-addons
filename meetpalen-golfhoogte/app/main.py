import csv
import io
import json
import logging
import os
import random
from datetime import datetime, timezone, timedelta
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import paho.mqtt.client as mqtt
import requests

CSV_URL = (
    "https://geo.rijkswaterstaat.nl/services/ogc/hws/wmdc15/ows"
    "?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature"
    "&TYPENAME=locatiesmetlaatstewaarneming&outputFormat=csv"
    "&FILTER=%3CFilter%3E%3CPropertyIsLike%20escape%3D'!'%20singleChar%3D'.'%20wildCard%3D'*'%3E%3CPropertyName%3EPARAMETER_WAT_OMSCHRIJVING%3C/PropertyName%3E%3CLiteral%3E*golfhoogte*%3C/Literal%3E%3C/PropertyIsLike%3E%3C/Filter%3E"
)

OPTIONS_PATH = "/data/options.json"
MIN_POLL_SECONDS = 600  # fair-use guardrail; data typically ~10m cadence
MAX_AGE_HOURS = 24  # discard stale readings older than this

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("meetpalen-golfhoogte")


@dataclass
class AddonConfig:
    broker_host: str
    broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_prefix: str = "homeassistant"
    poll_interval_seconds: int = 300
    station_codes: Optional[List[str]] = None

    @staticmethod
    def from_options(path: str = OPTIONS_PATH) -> "AddonConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return AddonConfig(
            broker_host=raw.get("broker_host", "mqtt"),
            broker_port=int(raw.get("broker_port", 1883) or 1883),
            mqtt_username=raw.get("mqtt_username"),
            mqtt_password=raw.get("mqtt_password"),
            mqtt_prefix=raw.get("mqtt_prefix", "homeassistant"),
            poll_interval_seconds=int(raw.get("poll_interval_seconds", 300) or 300),
            station_codes=raw.get("station_codes"),
        )


def build_mqtt_client(cfg: AddonConfig) -> mqtt.Client:
    client = mqtt.Client()
    if cfg.mqtt_username:
        client.username_pw_set(cfg.mqtt_username, cfg.mqtt_password or None)

    def on_connect(cl, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error("MQTT connection failed with code %s", rc)

    client.on_connect = on_connect

    client.connect(cfg.broker_host, cfg.broker_port, keepalive=60)
    client.loop_start()
    return client


def fetch_csv_rows() -> List[Dict[str, str]]:
    logger.debug("Fetching CSV from Rijkswaterstaat WFS")
    resp = requests.get(CSV_URL, timeout=30)
    resp.raise_for_status()
    # Ensure we have text and parse as CSV
    resp.encoding = resp.encoding or "utf-8"
    text = resp.text
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def normalize_station_codes(codes: Optional[List[str]]) -> Optional[List[str]]:
    if not codes:
        return None
    return [c.strip().upper() for c in codes if c and c.strip()]


def publish_discovery(client: mqtt.Client, cfg: AddonConfig, code: str, name: str, unit: str, state_topic: str, attr_topic: str, availability_topic: str):
    object_id = f"meetpalen_{code.lower()}_golfhoogte"
    topic = f"{cfg.mqtt_prefix}/sensor/{object_id}/config"
    payload = {
        "name": f"Golfhoogte {code}",
        "unique_id": object_id,
        "state_topic": state_topic,
        "availability_topic": availability_topic,
        "icon": "mdi:waves",
        "state_class": "measurement",
        "unit_of_measurement": unit or "cm",
        "device": {
            "identifiers": [f"meetpalen_{code}"],
            "manufacturer": "Rijkswaterstaat",
            "model": "WaterWebservices WFS",
            "name": f"Meetpaal {code}",
        },
        "json_attributes_topic": attr_topic,
    }
    # Retain discovery so HA picks it up even if HA restarts
    client.publish(topic, json.dumps(payload), qos=1, retain=True)


def publish_availability(client: mqtt.Client, cfg: AddonConfig, status: str):
    topic = f"{cfg.mqtt_prefix}/meetpalen/availability"
    client.publish(topic, status, qos=1, retain=True)


def publish_state(client: mqtt.Client, cfg: AddonConfig, code: str, value: Optional[float], timestamp: str, description: str, unit: str, raw_row: Dict[str, str]):
    base_id = f"meetpalen_{code.lower()}_golfhoogte"
    state_topic = f"{cfg.mqtt_prefix}/sensor/{base_id}/state"
    attr_topic = f"{cfg.mqtt_prefix}/sensor/{base_id}/attributes"
    availability_topic = f"{cfg.mqtt_prefix}/meetpalen/availability"

    publish_discovery(client, cfg, code, description, unit, state_topic, attr_topic, availability_topic)

    if value is None:
        payload_state = "unknown"
    else:
        payload_state = f"{value:.2f}"

    attributes = {
        "timestamp": timestamp,
        "description": description,
        "unit": unit,
        "station_code": code,
    }
    # Include a small subset of raw for troubleshooting
    for key in ("STATUSWAARDE", "KWALITEITSWAARDE_CODE", "GROOTHEIDCODE", "PARAMETERCODE"):
        if key in raw_row:
            attributes[key.lower()] = raw_row.get(key)

    client.publish(state_topic, payload_state, qos=1, retain=True)
    client.publish(attr_topic, json.dumps(attributes), qos=0, retain=True)


def parse_value(raw_value: str) -> Optional[float]:
    if raw_value is None:
        return None
    raw_value = raw_value.strip()
    if not raw_value:
        return None
    try:
        # Values are in cm; keep as float
        return float(raw_value)
    except ValueError:
        return None


def is_valid_measurement(value: Optional[float], quality_code: Optional[str], status: Optional[str]) -> bool:
    """
    Apply basic QA:
    - quality code must be "00" (valid)
    - skip sentinel/extreme values
    - skip unchecked/unknown status
    """
    if value is None:
        return False
    if quality_code and quality_code.strip() != "00":
        return False

    # Sentinel / bad values from feed
    if value >= 99999:
        return False

    # Discard extreme outliers (>4m) to avoid polluting HA
    if value > 400:
        return False

    # Treat unchecked/unknown status as invalid to keep feed clean
    if status and status.strip().lower() in {"ongecontroleerd", "onbekend"}:
        return False

    return True


def is_fresh_enough(timestamp_str: str, max_age_hours: int = MAX_AGE_HOURS) -> bool:
    """Return True if timestamp is within the max_age_hours window."""
    if not timestamp_str:
        return False
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except Exception:
        return False
    now = datetime.now(timezone.utc)
    age = now - dt.astimezone(timezone.utc)
    return age <= timedelta(hours=max_age_hours)


def main():
    cfg = AddonConfig.from_options()
    cfg.station_codes = normalize_station_codes(cfg.station_codes)
    logger.info("Starting Meetpalen golfhoogte add-on")
    client = build_mqtt_client(cfg)
    publish_availability(client, cfg, "online")

    base_interval = max(MIN_POLL_SECONDS, cfg.poll_interval_seconds)
    consecutive_failures = 0

    try:
        while True:
            try:
                rows = fetch_csv_rows()
                logger.info("Fetched %d rows", len(rows))
                for row in rows:
                    code = (row.get("CODE") or "").strip().upper()
                    if cfg.station_codes and code not in cfg.station_codes:
                        continue

                    value = parse_value(row.get("WAARDE_LAATSTE_METING"))
                    quality = (row.get("KWALITEITSWAARDE_CODE") or "").strip()
                    status = (row.get("STATUSWAARDE") or "").strip()
                    timestamp = (row.get("TIJDSTIP_LAATSTE_METING") or "").strip()
                    description = (row.get("PARAMETER_WAT_OMSCHRIJVING") or "Golfhoogte").strip()
                    unit = (row.get("EENHEIDCODE") or "cm").strip() or "cm"

                    if not code:
                        continue

                    if not is_valid_measurement(value, quality, status) or not is_fresh_enough(timestamp):
                        logger.debug(
                            "Marking %s as unknown due to QA/age filter (value=%s, quality=%s, status=%s, timestamp=%s)",
                            code,
                            value,
                            quality,
                            status,
                            timestamp,
                        )
                        value = None

                    publish_state(
                        client=client,
                        cfg=cfg,
                        code=code,
                        value=value,
                        timestamp=timestamp,
                        description=description,
                        unit=unit,
                        raw_row=row,
                    )
                consecutive_failures = 0
            except requests.HTTPError as err:
                logger.error("HTTP error while fetching CSV: %s", err)
                consecutive_failures += 1
            except requests.RequestException as err:
                logger.error("Network error while fetching CSV: %s", err)
                consecutive_failures += 1
            except Exception as err:  # noqa: BLE001
                logger.exception("Unexpected error while processing data: %s", err)
                consecutive_failures += 1

            # Fair-use: clamp to a minimum and add backoff on consecutive failures
            backoff = min(1800, base_interval * (2 ** min(consecutive_failures, 4)))
            jitter = random.uniform(0.9, 1.1)
            sleep_for = max(MIN_POLL_SECONDS, backoff) * jitter
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        logger.info("Stopping add-on")
    finally:
        publish_availability(client, cfg, "offline")
        client.loop_stop()
        with suppress_exception():
            client.disconnect()


class suppress_exception:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return True


if __name__ == "__main__":
    main()
