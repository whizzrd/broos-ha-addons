# Meetpalen golfhoogte → Home Assistant (MQTT)

Eenvoudige add-on voor Home Assistant 2025: haalt golfhoogte (laatste meting) uit Rijkswaterstaat en publiceert sensoren via MQTT Discovery. Alleen een MQTT-broker is nodig (bijv. de standaard Mosquitto add-on).

## Wat je krijgt
- Automatische entiteiten per meetpaal (naam “Golfhoogte <CODE>”, eenheid cm).
- Attributen met timestamp en broninfo.
- Add-on toont een melding in HA die uitlegt dat je de MQTT-integratie moet inschakelen; zonder die stap verschijnen de sensoren niet.

## Installatie – stap voor stap (niet-technisch)
Volg exact deze volgorde in Home Assistant 2025.11:

1) **Repository toevoegen**
   - Instellingen → Add-ons → Add-on Store → ⋮ rechtsboven → Repositories.
   - Plak `https://github.com/whizzrd/broos-ha-addons` → Add → Reload.

2) **MQTT-broker installeren**
   - Zoek “Mosquitto broker” → Installeren → Start.
   - Open Configuratie van Mosquitto → Voeg een gebruiker toe (gebruikers-tab of veld `logins`). Kies een eenvoudige gebruikersnaam/wachtwoord en noteer deze.

3) **Meetpalen add-on installeren**
   - Zoek “Meetpalen golfhoogte” in de Add-on Store (na de reload) → Installeren.
   - Configuratie invullen:
     - `broker_host`: `core-mosquitto` (als de broker op dezelfde HA draait) of het IP/host van je broker.
     - `broker_port`: 1883 (standaard).
     - `mqtt_username` / `mqtt_password`: de login uit stap 2.
     - `mqtt_prefix`: laten staan op `homeassistant` (voor discovery).
     - `poll_interval_seconds`: laten staan op 600 (bron wordt ~10 min ververst).
     - `station_codes`: leeg laten voor alle golfhoogte-stations; of bv. `["OSKS","MMND"]`.
   - Klik Save → Start.
   - Optioneel: schakel “Start on boot” en “Watchdog” in.

4) **MQTT-integratie inschakelen (essentieel)**
   - Ga naar Instellingen → Apparaten & Diensten.
   - Onder “Ontdekt” zie je een tegel “MQTT” (als die niet zichtbaar is: even op Reload klikken).
   - Klik de tegel → Inschakelen / Volgende / Gereed. Geen extra gegevens nodig als je Mosquitto op dezelfde HA hebt.
   - Zonder deze stap verschijnen de sensoren niet, ook al draait de add-on. De add-on plaatst een notificatie die naar deze stap verwijst.

5) **Sensoren bekijken**
   - Instellingen → Apparaten & Diensten → tab Entiteiten → filter op `meetpaal_`.
   - Voeg ze toe aan een dashboard: Overzicht → Bewerk dashboard → Kaart toevoegen → “Entiteiten” → selecteer de meetpaal-sensoren.

## Veelvoorkomende vragen
- **Ik zie geen entiteiten:** Controleer stap 4 (MQTT-integratie activeren) en herstart de meetpalen add-on. Kijk ook of je broker-gebruiker klopt.
- **“MQTT connection failed / code 5”:** Verkeerde gebruikersnaam/wachtwoord of broker-host. Pas de add-on config aan en herstart zowel Mosquitto als de meetpalen add-on.
- **Onrealistische waarden (bijv. 999999 cm):** De add-on stuurt dan `unknown` om de fout te overschrijven. QA-filter blokkeert waarden ≥ 99999 cm, > 400 cm, of zonder kwaliteitscode “00”, en met status “ongecontroleerd/onbekend”. Metingen ouder dan 24 uur worden ook genegeerd.
- **Polling-frequentie:** Minimaal 600 seconden met jitter/backoff, zodat de bron niet overbelast raakt.

## Technische details (ter info)
- Bron: Rijkswaterstaat WFS CSV `locatiesmetlaatstewaarneming`, filter op `PARAMETER_WAT_OMSCHRIJVING` bevat `golfhoogte`.
- Discovery: MQTT discovery met prefix `homeassistant`; retained config + retained state/attributes.
- Beschikbaarheid: `homeassistant/meetpalen/availability` (online/offline).
- Timestamps: direct uit de bron; metingen ouder dan 24 uur worden op `unknown` gezet.

## Problemen oplossen (kort)
1) Broker-user ontbreekt? Voeg een login toe in Mosquitto en herstart.
2) MQTT-integratie niet actief? Instellingen → Apparaten & Diensten → Ontdekt → MQTT → Inschakelen.
3) Nog steeds geen entiteiten? Herstart de meetpalen add-on en de MQTT-integratie; controleer de add-on log.
4) Oude foutieve waarden? Na de QA-filter wordt `unknown` gepubliceerd; wacht één polling-cyclus of herstart de add-on.
