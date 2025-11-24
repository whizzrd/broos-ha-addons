# Meetpalen golfhoogte → Home Assistant (MQTT)

Eenvoudige add-on voor Home Assistant 2025: haalt golfhoogte (laatste meting) uit Rijkswaterstaat en publiceert sensoren via MQTT Discovery. Alleen een MQTT-broker is nodig (bijv. de standaard Mosquitto add-on).

## Wat je krijgt
- Automatische entiteiten per meetpaal (naam “Golfhoogte <CODE>”, eenheid cm).
- Attributen met timestamp en broninfo.
- Add-on toont een melding in HA die uitlegt dat je de MQTT-integratie moet inschakelen; zonder die stap verschijnen de sensoren niet.

## Installatie – stap voor stap (niet-technisch, Home Assistant 2024/2025)
Volg elke klik; niets via terminal nodig. Benamingen kunnen iets afwijken per taal (in het Nederlands heet de “Add-on Store” bijv. **Add-onwinkel** en “Devices & Services” heet **Apparaten & Diensten**).

1) **Repository toevoegen**
   - Open HA → linkerzijbalk: **Instellingen** → **Add-ons** → **Add-on Store**/**Add-onwinkel**.
   - Rechtsboven: **⋮** → **Repositories** (of **Opslagplaatsen**). Dit opent een dialoog.
   - Plak deze link: `https://github.com/whizzrd/broos-ha-addons` → klik **Add**/**Toevoegen** → daarna **Reload**/**Herladen**. Wacht tot het herladen klaar is.

2) **MQTT-broker installeren en gebruiker maken**
   - In de Add-on Store/winkel: zoek **“Mosquitto broker”** → klik erop → **Installeren** → na installatie: **Start**.
   - Klik tab **Configuratie** in de Mosquitto add-on.
   - Onder **Gebruikers**: klik **+ Gebruiker toevoegen**.
     - Kies een gebruikersnaam, bv. `mqttuser`.
     - Kies een wachtwoord, bv. `mqttpass`.
     - Klik **Opslaan**/**Save**. Deze gegevens heb je zo nodig.

3) **Meetpalen add-on installeren en instellen**
   - Terug naar de Add-on Store/winkel: zoek **“Meetpalen golfhoogte”** → klik → **Installeren**.
   - Na installatie: open tab **Configuratie** en vul stap voor stap in (de UI toont per regel een invoerveld):
     - `broker_host`: typ `core-mosquitto` (als de broker op dezelfde HA draait). Laat je het veld leeg, dan zet de add-on het automatisch terug naar `core-mosquitto`.
     - `broker_port`: laat staan op **1883** (of vul 1883 in als het vak leeg is).
     - `mqtt_username`: de gebruikersnaam uit stap 2 (bijv. `mqttuser`).
     - `mqtt_password`: het wachtwoord uit stap 2 (bijv. `mqttpass`).
     - `mqtt_prefix`: laten staan op `homeassistant` (leeg veld wordt ook automatisch `homeassistant`).
     - `poll_interval_seconds`: laten staan op **600** (getal in seconden).
     - `station_codes`: het veld lijkt verplicht in de UI; voer minimaal één code in. Je kunt de kant-en-klare lijst hieronder kopiëren zodat alle gangbare golfmeetstations meteen worden gepubliceerd.
   - Klik **Opslaan**/**Save**. Controleer of er geen rode foutmeldingen meer staan.
   - Ga naar tab **Info** → zet aan: **Start on boot**/**Opstarten** en **Watchdog** (optioneel maar handig).
   - Klik **Start** om de add-on te draaien. Wacht tot de status op **Running**/**Actief** komt te staan.

### Kant-en-klare lijst met golfmeetstations
Home Assistant dwingt een niet-lege `station_codes`-waarde af. Plak onderstaande JSON direct in het veld om alle courante golfhoogte-meetpunten (Rijkswaterstaat, november 2025) te ontvangen. Je mag de lijst later inkorten tot de stations die je echt nodig hebt.

```
["EPL","LEG","HKVH","IJMD","MPN","OSKS","MMND","K13","ODNZ","VLIS"]
```

| Code  | Locatie / omschrijving              |
|-------|-------------------------------------|
| EPL   | Europlatform (Noordzee)             |
| LEG   | Lichteiland Goeree                  |
| HKVH  | Hoek van Holland                    |
| IJMD  | IJmuiden Munitiestort               |
| MPN   | Meetpost Noordwijk                  |
| OSKS  | Oosterscheldekering Schouwen        |
| MMND  | Maasmonding Noord                   |
| K13   | Boorplatform K13 (Noordzee)         |
| ODNZ  | Oudeschild Noordzee                 |
| VLIS  | Vlissingen boei (Westerschelde)     |

4) **MQTT-integratie inschakelen (anders geen sensoren)**
   - Linkerzijbalk: **Instellingen** → **Apparaten & Diensten**.
   - Wacht 5–10 seconden; onder kopje **Ontdekt**/**Discovered** verschijnt een tegel **MQTT**.
   - Klik de tegel **MQTT** → **Inschakelen**/**Enable** (of **Configureer** → **Inschakelen** → **Volgende** → **Gereed**).
   - Als de tegel niet verschijnt: klik rechtsboven **Reload**/**Herladen** en kijk opnieuw. De add-on stuurt ook een melding die naar deze stap verwijst.

5) **Sensoren vinden en op een dashboard zetten**
   - **Instellingen**/**Settings** → **Apparaten & Diensten**/**Devices & Services** → tab **Entiteiten**/**Entities**.
   - Zoek op `meetpalen_` in de zoekbalk. Je ziet de meetpaal-sensoren (bijv. `sensor.meetpalen_oskx_golfhoogte`).
   - Voeg ze toe aan een dashboard: **Overzicht** → rechtsboven **Bewerken dashboard**/**Edit dashboard** → **Kaart toevoegen** → kies kaart **Entiteiten** → selecteer de meetpaal-sensoren → **Opslaan**/**Save**.


## Veelvoorkomende vragen
- **Ik zie geen entiteiten:** Controleer stap 4 (MQTT-integratie activeren) en herstart de meetpalen add-on. Kijk ook of je broker-gebruiker klopt. Zie ook de checklist hieronder om gericht te testen.
- **“MQTT connection failed / code 5”:** Verkeerde gebruikersnaam/wachtwoord of broker-host. Pas de add-on config aan en herstart zowel Mosquitto als de meetpalen add-on.
- **Onrealistische waarden (bijv. 999999 cm):** De add-on stuurt dan `unknown` om de fout te overschrijven. QA-filter blokkeert waarden ≥ 99999 cm, > 400 cm, of zonder kwaliteitscode “00”, en met status “ongecontroleerd/onbekend”. Metingen ouder dan 24 uur worden ook genegeerd.
- **Polling-frequentie:** Minimaal 600 seconden met jitter/backoff, zodat de bron niet overbelast raakt.

### Checklist als er toch geen entiteiten opduiken
1. Open de add-on → tab **Logboek**/**Log**. Zoek een regel `Connected to MQTT broker`. Ontbreekt die, controleer host/poort/gebruikersnaam in de configuratie en of Mosquitto draait.
2. Kijk of er een Home Assistant-melding is met de tekst “Zorg dat de MQTT-integratie actief is…”. Zo niet, ga naar **Instellingen** → **Apparaten & Diensten** → **Ontdekt**/**Discovered** en activeer de tegel **MQTT** handmatig.
3. Herstart de add-on na het aanpassen van de configuratie. Na de herstart hoort in het log `Fetched <aantal> rows` te staan; zie je 0 rijen of fouten, probeer het na enkele minuten opnieuw.
4. Controleer in **Instellingen** → **Apparaten & Diensten** → tab **Entiteiten**/**Entities** of er filters actief zijn. Zoeken op `meetpalen_` toont alleen de sensoren wanneer de MQTT-integratie actief is.

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
