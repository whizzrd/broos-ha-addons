### 2025-01-xx – Meetpalen add-on UX
  - Aanpassing: bij start een persistente notificatie met de MQTT-installatiestap (Instellingen → Apparaten & Diensten → Ontdekt → MQTT → Inschakelen).
  - Implementatie: `app/main.py` kreeg `notify_setup_needed()` (Supervisor token) en `config.json` versie 0.1.2.
  - README-installatie herschreven voor HA 2025.11 met klik-voor-klik instructies voor niet-technische gebruikers.
  - Status: code gecommit en gepusht naar GitHub; HA-side update uitvoeren via Add-on Store → Reload → Update/Restart.
