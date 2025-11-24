### 2025-01-?? – Meetpalen add-on UX
  - Aanpassing: add-on plaatst bij start een persistente notificatie met de MQTT-installatiestap (Instellingen → Apparaten & Diensten → Ontdekt → MQTT → Inschakelen).
  - Implementatie: `app/main.py` kreeg `notify_setup_needed()` (Supervisor token) en `config.json` versie 0.1.2.
  - README-installatie bijgewerkt (repo in store, melding over notificatie).
  - Status: code lokaal aangepast; push naar GitHub + update in HA nog uitvoeren.
