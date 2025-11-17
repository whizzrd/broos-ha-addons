# Broos Home Assistant Add-ons

Repository with one or more Home Assistant add-ons. Current add-on: **Meetpalen golfhoogte** (publishes Rijkswaterstaat golfhoogte via MQTT discovery).

## Install this repository in HA
1) Copy the repo URL (replace with your GitHub URL, e.g. `https://github.com/whizzrd/broos-ha-addons`).
2) In HA: Settings → Add-ons → Add-on Store → ⋮ → Repositories → paste the URL → Add → Reload.
3) The add-ons from this repo appear in the store list.

## Install “Meetpalen golfhoogte”
1) Ensure an MQTT broker runs (e.g. Mosquitto add-on) and has a user/password.
2) In the Add-on Store, open “Meetpalen golfhoogte” → Install.
3) Configuration:
   - `broker_host`: typically `core-mosquitto`.
   - `broker_port`: default 1883.
   - `mqtt_username` / `mqtt_password`: the broker login you created.
   - `mqtt_prefix`: leave `homeassistant`.
   - `poll_interval_seconds`: keep ≥ 600.
   - `station_codes`: leave empty for all, or list codes (e.g., `["OSKS","MMND"]`).
4) Save → Start → check logs for “Connected to MQTT broker”.
5) Add the MQTT integration: Settings → Devices & Services → click the “MQTT” discovery tile → Submit. Without this, entities won’t appear.

## Troubleshooting
- Auth errors (code 5): fix broker user/pass in add-on config; restart broker and add-on.
- No entities: reload MQTT integration, then Developer Tools → States filter `meetpaal_`.
- Unrealistic values: add-on QA filters bad data; invalid readings are published as `unknown` to clear retains.
