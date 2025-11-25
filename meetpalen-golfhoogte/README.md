# Meetpalen golfhoogte → Home Assistant (MQTT)

Eenvoudige add-on voor Home Assistant 2025: haalt golfhoogte (laatste meting) uit Rijkswaterstaat en publiceert sensoren via MQTT Discovery. Alleen een MQTT-broker is nodig (bijv. de standaard Mosquitto add-on).

## Wat je krijgt
- Automatische entiteiten per meetpaal (naam `<CODE> - Golfhoogte`, eenheid m). Code staat vooraan zodat je stations in het dashboard kunt onderscheiden.
- Attributen met timestamp en broninfo.
- Add-on toont een melding in HA die uitlegt dat je de MQTT-integratie moet inschakelen; zonder die stap verschijnen de sensoren niet.

## Installatie – stap voor stap (niet-technisch, Home Assistant 2024/2025)
Volg elke klik; niets via terminal nodig. Benamingen kunnen iets afwijken per taal (in het Nederlands heet de “Add-on Store” bijv. **Add-onwinkel** en “Devices & Services” heet **Apparaten & Diensten**).

1) **Repository toevoegen**
   - Open HA → linkerzijbalk: **Instellingen** → **Add-ons** → **Add-on-winkel** (Engels: **Add-on Store**).
   - Rechtsboven: knop **Menu** (⋮) → **Repositories** (NL kan ook **Opslagplaatsen** heten). Dialoogtitel: “**Beheer de add-onrepositories**”.
   - Veld **Toevoegen**: plak `https://github.com/whizzrd/broos-ha-addons` → klik **Toevoegen** → klik **Sluiten**. Vraagt HA om herladen? klik **Herladen/Reload**.

2) **MQTT-broker installeren en gebruiker maken**
   - In de Add-on-winkel: zoek **“Mosquitto broker”** → open → **Installeren**.
   - Na installatie, tab **Configuratie** → sectie **Logins** → klik **Toevoegen**:
     - Gebruikersnaam: `mqttuser`.
     - Wachtwoord: `mqttpass`.
     - Klik **Opslaan** in de dialoog. Herhaal **Toevoegen** als je extra logins wilt.
   - Tab **Informatie**: zet **Start bij opstarten** en **Watchdog** aan → klik **starten**. Wacht tot status **Actief/Running** is.

3) **Meetpalen add-on installeren en instellen**
   - Terug naar de Add-on-winkel: zoek **“Meetpalen golfhoogte”** → open → **Installeren**.
   - Tabbladen bovenaan: **Informatie**, **Configuratie**, **Logboek**.
   - Tab **Configuratie** (velden met * zijn verplicht):
     - `broker_host*`: `core-mosquitto`.
     - `broker_port*`: **1883**.
     - `mqtt_username*`: de gebruiker uit stap 2 (bijv. `mqttuser`).
     - `mqtt_password*`: het wachtwoord (bijv. `mqttpass`).
     - `mqtt_prefix*`: `homeassistant`.
     - `poll_interval_seconds*`: **600**.
     - `station_codes*`: UI eist niet-leeg; typ een code en druk **Enter** zodat er een “chip” verschijnt. Voeg meerdere codes één-voor-één toe (bijv. `EPL, LEG, HKVH, IJMD, MPN, OSKS, MMND, K13, ODNZ, VLIS`).
   - Klik **Opslaan** (knop onderaan) en kies **Herstart** in de pop-up, zodat de nieuwe codes actief zijn.
   - Tab **Informatie**: zet de schakelaars **Start bij opstarten** en **Watchdog** aan.
   - Knoppen op **Informatie**: **starten**, **Verwijderen**, **Herbouw**. Klik **starten** en wacht tot de status **Actief/Running** is.

### Kant-en-klare lijst met golfmeetstations
Home Assistant dwingt een niet-lege `station_codes`-waarde af. Plak onderstaande JSON direct in het veld om alle courante golfhoogte-meetpunten (Rijkswaterstaat, november 2025) te ontvangen. Je mag de lijst later inkorten tot de stations die je echt nodig hebt. Alleen stations met recente metingen verschijnen; op 25 nov 2025 heeft de bron o.a. data voor `K13`, `LEG`, `MMND`, `OSKS`.

```
["EPL","LEG","HKVH","IJMD","MPN","OSKS","MMND","K13","ODNZ","VLIS"]
```

> IJsselmeer/Markermeer: de RWS-laag `locatiesmetlaatstewaarneming` bevat wel golfhoogte-meetpalen (bijv. `IJSSMMPL02`, `09`, `26`, `29`, `37`, `42`, `44`, `46`, `47`, `48`, `49`), maar alle laatst gemeten timestamps zijn oud (2007–2019). De add-on filtert metingen ouder dan 24 uur weg, dus deze stations verschijnen niet en tonen geen kaart. Voeg ze niet toe aan `station_codes` tenzij de bron opnieuw actuele golfhoogte publiceert.

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
   - Linkerzijbalk: **Instellingen** → **Apparaten & Diensten** → tab **Integraties**/**Integrations**.
   - Onder kop **Ontdekt**/**Discovered**: tegel **MQTT** → klik **Toevoegen**. Banner verschijnt: “**MQTT Broker via Home Assistant add-on**” met knoppen **Verzenden** en daarna “**Gelukt**” → **Voltooien**.
   - Als de tegel niet verschijnt: klik rechtsboven **Reload**/**Herladen** en kijk opnieuw. De add-on stuurt ook een melding die naar deze stap verwijst.
   - Controle: **Instellingen → Apparaten & Diensten → Integraties → MQTT**. Daar horen apparaten te staan zoals “Significante golfhoogte … (K13)”.

5) **Sensoren vinden en op een dashboard zetten**
   - **Instellingen**/**Settings** → **Apparaten & Diensten**/**Devices & Services** → tab **Entiteiten**/**Entities**.
   - Zoek op `golfhoogte` of open de MQTT-integratie en klik op **X entiteiten**. Je ziet de meetpaal-sensoren (bijv. `(K13)`, `(LEG)`). Duurt het even? Wacht een minuut en check het add-on **Logboek** op “Connected to MQTT broker” en “Fetched … rows”.
   - Dashboard: ga naar **Overzicht**.
     - Klik rechtsboven **Dashboard bewerken** (drie-puntenmenu → **Controle nemen** als HA dat vraagt) → **Kaart toevoegen**.
     - Kies kaart **Entiteiten** → verwijder de voorbeeld-entiteiten met **Wissen** → klik **Entiteit toevoegen** en selecteer de golfhoogte-sensoren → **Opslaan** → **Klaar**.
     - Tip: Alleen stations met een recente meting verschijnen; de kaart kan dus minder items tonen dan je `station_codes`-lijst.

## Add-on updaten in Home Assistant
- **Add-on-winkel** → rechtsboven **Menu (⋮)** → **Naar updates zoeken**.
- Open **Meetpalen golfhoogte** → knop **Update** → wacht tot de installatie klaar is → **Herstarten** (of **starten**). De add-on publiceert daarna de nieuwe discovery/state berichten.
- Zie je oude entiteiten/kaarten? Herstart de add-on nogmaals om retained MQTT-berichten te verversen en verwijder dubbele kaarten in **Dashboard bewerken**.


## Veelvoorkomende vragen
- **Ik zie geen entiteiten:** Controleer stap 4 (MQTT-integratie activeren) en herstart de meetpalen add-on. Kijk ook of je broker-gebruiker klopt. Zie ook de checklist hieronder om gericht te testen.
- **“MQTT connection failed / code 5”:** Verkeerde gebruikersnaam/wachtwoord of broker-host. Pas de add-on config aan en herstart zowel Mosquitto als de meetpalen add-on.
- **Onrealistische waarden (bijv. 999999 cm):** De add-on stuurt dan `unknown` om de fout te overschrijven. QA-filter blokkeert waarden ≥ 99999 cm, > 400 cm, of zonder kwaliteitscode “00”. Metingen ouder dan 24 uur worden ook genegeerd. Status “ongecontroleerd” wordt toegelaten (anders mist je recente data); alleen “onbekend” wordt weggefilterd.
- **Polling-frequentie:** Minimaal 600 seconden met jitter/backoff, zodat de bron niet overbelast raakt.

### Checklist als er toch geen entiteiten opduiken
1. Open de add-on → tab **Logboek**/**Log**. Zoek een regel `Connected to MQTT broker`. Ontbreekt die, controleer host/poort/gebruikersnaam in de configuratie en of Mosquitto draait.
2. Kijk of er een Home Assistant-melding is met de tekst “Zorg dat de MQTT-integratie actief is…”. Zo niet, ga naar **Instellingen** → **Apparaten & Diensten** → **Ontdekt**/**Discovered** en activeer de tegel **MQTT** handmatig.
3. Herstart de add-on na het aanpassen van de configuratie. Na de herstart hoort in het log `Fetched <aantal> rows` te staan; zie je 0 rijen of fouten, probeer het na enkele minuten opnieuw.
4. Controleer in **Instellingen** → **Apparaten & Diensten** → tab **Entiteiten**/**Entities** of er filters actief zijn. Zoeken op `golfhoogte` of `meetpalen_` toont de sensoren wanneer de MQTT-integratie actief is.
5. Zie je slechts een paar stations? De bron `locatiesmetlaatstewaarneming` geeft alleen meetpunten met een recente meting; stations zonder actuele data worden niet gepubliceerd.

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
