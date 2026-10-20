# Docentnotities: Jouw stem, hun scam (150 min)

Tweedejaars HBO-ICT, blok "De schaduwkant van technologie". Studenten werken in paren, ieder op een eigen laptop, met hun eigen stem. Al het zware werk draait in Google Colab; jouw laptop draait de luistertest.

## Voor de les

**De dag ervoor (dry run)**
- [ ] Volg de checklist in `dry-run.md` en noteer de uitkomsten.
- [ ] Maak je eigen demoset met `demo-script.md`.

**Een uur voor de les**
- [ ] `make setup-test` (eenmalig), daarna `make pair-codes`. Print de paarkaarten (20 stuks, 2 per A4-rij) en knip ze uit.
- [ ] Laptop aan de stroom, slaapstand uit.
- [ ] `make serve-test`. Accepteer de macOS-firewallmelding ("inkomende verbindingen toestaan").
- [ ] Open op je telefoon (op het klaswifi) de URL die in de terminal staat. Werkt dat niet? Zet je hotspot aan, verbind je laptop ermee en start `make serve-test` opnieuw.
- [ ] Open `/resultaten` op de beamer, in een apart venster.
- [ ] Zet de Colab-link (zie README) op de eerste slide, met een QR-code.

## Minuut voor minuut

### 0:00–0:15 Hook
- **0:00** Deel de paarkaarten uit. "Open de link op het scherm en start meteen cel 1, die duurt een paar minuten."
- **0:02** "Voor we beginnen: ik kreeg vanochtend een spraakbericht..." Speel je demokloon af (`demo-script.md`), zonder iets te zeggen over AI.
- **0:04** Onthulling: "Dat was ik niet. Dat was een model, gevoed met 10 seconden van mijn stem, gemaakt op een gratis laptop in de cloud."
- **0:06** De nieuwszaken (slides 3–5): INTERPOL-campagne (18 okt), de Britse AI-scam-watchlist (19 okt), de Californische moeder die $5.400 verloor aan een nep-ontvoeringsgesprek met de gekloonde stem van haar dochter (7 okt).
- **0:13** Kijk rond: staat cel 1 overal te draaien?

### 0:15–0:25 Toestemming en setup
- Laat iedereen stap 2 lezen en invullen. Benadruk: alleen je eigen stem, niets delen, alles wordt gewist.
- **Opt-out:** wie niet wil opnemen of geen Google-account wil gebruiken, kijkt mee bij de partner en beoordeelt wel mee in de luistertest. Of gebruik jouw demoset.
- Loop rond: staat er in cel 1 onderaan "✅ Alles werkt"?
  - **❌ Geen GPU:** *Runtime → Runtimetype wijzigen → T4 GPU* en cel 1 opnieuw. Lukt het niet, dan werkt het paar op één runtime (eerst A neemt alles op en downloadt, dan B: stap 2 opnieuw met de andere letter).
  - **❌ bij installeren:** noteer de melding. Laat het paar samenwerken op de andere laptop.

### 0:25–1:10 Bouwen
- **3a leestekst:** de browser vraagt microfoontoegang. Tip: stille hoek, laptop dichtbij, normaal tempo.
- **3b testzin:** één keer de zin voorlezen. Dit wordt de "echte" clip in de luistertest.
- **4 experiment:** 12 klonen. Op een T4 duurt dat een paar minuten. Laat ze de generatietijd en de realtime-factor bekijken: "Hoe lang duurt het om iemand te laten zeggen wat je wilt?"
- **Gesprekspunt, het 10-secondenplafond:** Chatterbox gebruikt nooit meer dan 10 seconden van een stem (6 s voor de stemkenmerken, 10 s voor de klank). Meer audio maakt de kloon niet beter. Een Instagram-story is dus genoeg.
- **5 vrije modus:** laat ze spelen. Teksten met geld, codes of ontvoering worden geweigerd; bespreek waarom dat filter makkelijk te omzeilen is.
- **6 downloaden:** de zip `CODE-A.zip` staat in hun downloadmap.

### 1:10–1:20 Pauze
Experimenten die nog lopen, lopen gewoon door.

### 1:20–1:45 Blinde luistertest
- Zet de luistertest-URL en QR-code op het scherm.
- **1:20** "Upload je zip via *Clips uploaden*." Iedere spreker uploadt zijn of haar eigen zip.
- **1:25** "Ga naar *Beoordelen*, vul je paircode in, en beoordeel zoveel clips als je kunt: echt of nep?" Je hoort nooit clips van je eigen paar.
- Laat `/resultaten` live meelopen op de beamer.
- **1:40** Klik op *Onthul*. Bespreek:
  - Werd de 3 s-kloon vaker herkend dan de 10 s-kloon?
  - Werd de echte stem soms voor nep aangezien? Waarom? (Laptopmicrofoon, ruis, voorleesstem.)
  - **Ruis als verraad:** de echte opname bevat kamergeluid, de kloon niet. Dat is een hint, geen bewijs: een oplichter voegt zo ruis toe, en over de telefoon valt het weg.

### 1:45–2:10 Detectie
- Laat iedereen stap 7 draaien en de samenvatting bekijken.
- Verwachting (controleer in de dry run, `dry-run.md`):
  - **Watermerk:** ongeveer 1,0 op klonen en 0,0 op echte clips, en het overleeft MP3. Na de telefoonlijn was het in de test van 20 oktober weg (0,02).
  - **Classifier:** herkende in die test de klonen, maar na de telefoonlijn noemde hij alles "echt". Verwacht ook fouten op echte stemmen: hij is getraind op oudere deepfakes.
  - Kernpunt: precies het kanaal dat oplichters gebruiken (de telefoon) schakelt beide detectoren uit.
- Vraag: "Het watermerk werkt alleen omdat Resemble AI het erin stopt. Wat als de oplichter een ander open model gebruikt?"

### 2:10–2:30 Ethiek, wet en wissen
Discussievragen (slide 9):
1. Je stem staat op Instagram, je voicemail en opnames van colleges. Wie is verantwoordelijk als hij gekloond wordt: het platform, de modelmaker of de oplichter?
2. Artikel 50 van de AI Act verplicht dat deepfakes gelabeld zijn en dat synthetische audio machinaal herkenbaar is. Overleefde het watermerk de telefoonlijn? Wat doet een label in een live telefoongesprek?
3. Het model is open source (MIT-licentie), en andere open modellen hebben helemaal geen watermerk. Moeten ze open zijn?
4. Het model gebruikt maximaal 10 seconden van je stem. Hoeveel clips van 10 seconden van jou staan er online?
5. Een familie-"wachtwoord" verslaat de meeste van deze scams. Waarom is die low-tech oplossing sterker dan de detector?

**2:25 Wissen, samen:**
1. Iedereen draait stap 8, vinkt het vakje aan en klikt *Alles wissen*. Dit verwijdert de opnames en daarna de runtime.
2. Iedereen kiest *Bewerken → Alle uitvoer wissen* en sluit het tabblad zonder op te slaan.
3. Jij stopt de server (Ctrl+C) en draait `make wipe-test` (antwoord `y`).
4. Vraag of iemand een kopie in Drive heeft opgeslagen. Zo ja: laat diegene het bestand in Drive verwijderen.
5. Gedownloade zips: laat studenten ze uit hun downloadmap verwijderen.

## Noodplannen

| Probleem | Wat je doet |
| --- | --- |
| Paar krijgt geen GPU | Samen op één runtime; of jouw demoset gebruiken. |
| Installatie breekt | Zet in cel 1 vóór de installatie een regel `%env VCL_FULL_INSTALL=1`, verwijder `/content/.vcl_installed`, draai cel 1, en daarna *Runtime → Sessie opnieuw starten* en cel 1 nogmaals. Duurt langer. |
| Audiospeler blijft leeg | Zet in cel 1 `PLAYER` op `embed`. Let op: de audio staat dan in de uitvoer, dus *Alle uitvoer wissen* is verplicht. |
| Microfoon werkt niet | Andere browser (Chrome), of opnemen op de laptop van de partner. |
| Nederlands klinkt slecht | Gebruik de Engelse zinnen (EN1, EN2) in het gesprek; de luistertest blijft NL1. |
| Classifier laadt niet | Ga door met alleen het watermerk en het eigen oor. |
| Klaswifi blokkeert de luistertest | Telefoonhotspot. Of speel clips af op de beamer en laat de klas met handopsteken stemmen. |

## Wat de tools wel en niet afdwingen

De stappen weigeren te werken zonder toestemming, klonen kan alleen met een referentie die live in stap 3 is opgenomen (gecontroleerd met een hash), en de vrije modus weigert scamachtige tekst. Studenten kunnen in Colab wel zelf Python schrijven en die regels dus omzeilen. Het zijn vangrails, geen sloten. Benoem dat gerust: het is precies het punt van de les.
