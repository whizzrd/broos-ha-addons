# Meetpalen golfhoogte → Home Assistant (MQTT)

Eenvoudige add-on voor Home Assistant 2025: haalt golfhoogte (laatste meting) uit Rijkswaterstaat en publiceert sensoren via MQTT Discovery. Alleen een MQTT-broker is nodig (bijv. de standaard Mosquitto add-on).

## Wat je krijgt
- Automatische entiteiten per meetpaal (naam “Golfhoogte <CODE>”, eenheid cm).
- Attributen met timestamp en broninfo.
- Add-on toont een melding in HA die uitlegt dat je de MQTT-integratie moet inschakelen; zonder die stap verschijnen de sensoren niet.

## Installatie – stap voor stap (niet-technisch, Home Assistant 2025.11)
Volg elke klik; niets via terminal nodig.

1) **Repository toevoegen**
   - Open HA → linkerzijbalk: **Instellingen** → **Add-ons** → **Add-on Store**.
   - Rechtsboven: **⋮** → **Repositories**.
   - Plak deze link: `https://github.com/whizzrd/broos-ha-addons` → **Add** → daarna **Reload**.

2) **MQTT-broker installeren en gebruiker maken**
   - In de Add-on Store: zoek **“Mosquitto broker”** → klik erop → **Installeren** → na installatie: **Start**.
   - Klik **Configuratie** (tab in de Mosquitto add-on).
   - Onder **Gebruikers**: klik **+ Gebruiker toevoegen**.
     - Kies een gebruikersnaam, bv. `mqttuser`.
     - Kies een wachtwoord, bv. `mqttpass`.
     - Klik **Opslaan**. Deze gegevens heb je zo nodig.

3) **Meetpalen add-on installeren en instellen**
   - Terug naar de Add-on Store: zoek **“Meetpalen golfhoogte”** → klik → **Installeren**.
   - Na installatie: open tab **Configuratie** en vul in:
     - `broker_host`: `core-mosquitto` (als de broker op dezelfde HA draait). Alleen wijzigen als je een externe broker hebt.
     - `broker_port`: **1883** laten staan.
     - `mqtt_username`: de gebruikersnaam uit stap 2 (bijv. `mqttuser`).
     - `mqtt_password`: het wachtwoord uit stap 2 (bijv. `mqttpass`).
     - `mqtt_prefix`: laten staan op `homeassistant`.
     - `poll_interval_seconds`: laten staan op **600**.
     - `station_codes`: leeg laten voor alle stations, of vul codes in zoals `["OSKS","MMND"]`.
   - Klik **Opslaan**.
   - Ga naar tab **Info** → zet aan: **Start on boot** en **Watchdog** (optioneel maar handig).
   - Klik **Start** om de add-on te draaien.

4) **MQTT-integratie inschakelen (anders geen sensoren)**
   - Linkerzijbalk: **Instellingen** → **Apparaten & Diensten**.
   - Wacht 5–10 seconden; onder kopje **Ontdekt** verschijnt een tegel **MQTT**.
   - Klik de tegel **MQTT** → **Inschakelen** (of **Configureer** → **Inschakelen** → **Volgende** → **Gereed**).
   - Als de tegel niet verschijnt: klik rechtsboven **Reload** en kijk opnieuw. De add-on stuurt ook een melding die naar deze stap verwijst.

5) **Sensoren vinden en op een dashboard zetten**
   - **Instellingen** → **Apparaten & Diensten** → tab **Entiteiten**.
   - Zoek op `meetpaal_` in de zoekbalk. Je ziet de meetpaal-sensoren (bijv. `sensor.meetpalen_oskx_golfhoogte`).
   - Voeg ze toe aan een dashboard: **Overzicht** → rechtsboven **Bewerken dashboard** → **Kaart toevoegen** → kies kaart **Entiteiten** → selecteer de meetpaal-sensoren → **Opslaan**.

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
