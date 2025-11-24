# Meetpalen golfhoogte → Home Assistant (MQTT)

Eenvoudige Home Assistant add-on: haalt golfhoogte (laatste meting) uit Rijkswaterstaat WFS CSV en publiceert sensoren via MQTT Discovery. Alles draait in één container; alleen een MQTT-broker is nodig.

## Wat doet het
- Brontype: WFS CSV `locatiesmetlaatstewaarneming` gefilterd op `golfhoogte`.
- Publiceert per meetpaal een sensor met waarde (cm) en attribuut timestamp.
- MQTT Discovery zorgt dat sensoren automatisch verschijnen in Home Assistant.

## Installatie (HA OS / Supervised)
1) Voeg deze repo toe aan de Add-on Store: Instellingen → Add-ons → Add-on Store → ⋮ → Repositories → `https://github.com/whizzrd/broos-ha-addons` → Add → Reload.
2) Installeer de Mosquitto broker add-on en voeg een gebruiker toe (UI: gebruikers-tab in Mosquitto; of voeg login onder `logins`).
3) Installeer “Meetpalen golfhoogte”.
4) Configuratie invullen:
   - `broker_host`: meestal `core-mosquitto` (zelfde host) of ander broker-adres.
   - `broker_port`: 1883 (pas aan indien afwijkend).
   - `mqtt_username` / `mqtt_password`: de broker-login uit stap 2.
   - `mqtt_prefix`: laat op `homeassistant` voor discovery.
   - `poll_interval_seconds`: minimaal 600 (10 minuten is de broncadans).
   - `station_codes`: lijst, bijv. `["OSKS","MMND"]`; leeg = alle golfhoogte-stations.
5) Save en Start; bekijk het logboek voor connectie/fetch.
6) Ga naar Instellingen → Apparaten & Diensten en activeer de “MQTT” integratie (tegel “MQTT” onder Ontdekt → Inschakelen). Zonder integratie verschijnen de entiteiten niet. De add-on toont een melding in HA die naar deze stap verwijst.

## Config veldreferentie
- `broker_host` (str) — MQTT host.
- `broker_port` (int, default 1883).
- `mqtt_username` / `mqtt_password` (optioneel).
- `mqtt_prefix` (default `homeassistant`) — discovery prefix.
- `poll_interval_seconds` (default 600) — minimaal 600s enforced + jitter/backoff.
- `station_codes` (array[str]) — filter op meetpaal CODE; leeg laat alles door.

## Werking / techniek
- Endpoint:  
  `https://geo.rijkswaterstaat.nl/services/ogc/hws/wmdc15/ows?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&TYPENAME=locatiesmetlaatstewaarneming&outputFormat=csv&FILTER=<Filter><PropertyIsLike escape='!' singleChar='.' wildCard='*'><PropertyName>PARAMETER_WAT_OMSCHRIJVING</PropertyName><Literal>*golfhoogte*</Literal></PropertyIsLike></Filter>`
- Belangrijke velden: `CODE`, `WAARDE_LAATSTE_METING` (cm), `TIJDSTIP_LAATSTE_METING`, `EENHEIDCODE`, `PARAMETER_WAT_OMSCHRIJVING`.
- MQTT topics: availability + per sensor state/attributes; discovery retained.

## Fair use
- Bronupdate is ~10 minuten; de add-on handhaaft minimaal 600s polling met jitter en exponentiële backoff bij fouten om belasting te beperken.

## Uitbreidingen (optioneel)
- Historische data via WaterWebservices POST (`OphalenWaarnemingen`, grootheid Hm0).
- Converteer naar meters, meer parameters (bijv. piekperiode) als extra sensoren.

## Kwaliteitscontrole
- Alleen waarden met `KWALITEITSWAARDE_CODE == "00"` worden als state gepubliceerd.
- Sentinel/extreme waarden (`>= 99999` of > 400 cm) worden genegeerd en als `unknown` gepubliceerd zodat foutieve retains worden overschreven.
- Status `ongecontroleerd`/`onbekend` wordt genegeerd; attributen blijven aanwezig voor debugging.
- Waarden ouder dan 24 uur worden genegeerd (state wordt `unknown`).

## Checklist & troubleshooting (HA OS / Supervised)
1) Broker login: zorg dat de Mosquitto add-on een gebruiker heeft (UI: voeg login toe; in `/mnt/data/supervisor/addons/data/core_mosquitto/options.json` moet `logins` niet leeg zijn).
2) Voeg de MQTT-integratie toe in HA (Instellingen → Apparaten & Diensten → tegel “MQTT” → Add/Submit). Zonder integratie verschijnen de sensoren niet, ook al publiceert de add-on discovery.
3) Lokale add-on zichtbaar? In de Add-on Store: ⋮ → Reload nadat de map onder `/mnt/data/supervisor/addons/local/` staat.
4) MQTT auth errors (code 5): controleer user/wachtwoord in de add-on config en herstart Mosquitto + de meetpalen add-on.
5) Geen entities zichtbaar? Reload de MQTT-integratie en check Developer tools → States met filter `meetpaal_`.
6) Onrealistische waarden? QA-filter zet ze op `unknown`; bekijk attributen zoals `kwaliteitswaarde_code` en `statuswaarde`.

## Is dit haalbaar voor niet-technische gebruikers?
- Vereist nog handmatige stappen in de HA UI: brokergebruiker aanmaken én de MQTT-integratie toevoegen. Zonder die twee komen de sensoren niet door, wat voor niet-technische gebruikers verwarrend is.
- Voor “plug-and-play” zouden extra hulpmiddelen nodig zijn (bijv. add-on repository met vooraf ingestelde credentials + automatische MQTT-integratie via Supervisor API). In de huidige vorm is een korte install-checklist of begeleiding aanbevolen.
