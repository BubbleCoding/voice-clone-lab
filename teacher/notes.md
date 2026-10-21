# Docentnotities: Jouw stem, hun scam (150 min)

Tweedejaars ICT, blok "De schaduwkant van technologie". Studenten werken in paren, ieder op een eigen laptop, met hun eigen stem. Al het rekenwerk draait in Google Colab; je hebt zelf alleen de beamer en je slides nodig.

**Doel van de les:** studenten ervaren hoe makkelijk het is om een stem te klonen, en praten over de schaduwkant: oplichting, wie verantwoordelijk is, en wat wel en niet beschermt. Het notebook is het middel; de gesprekken zijn de kern. Daarom zitten er vier gespreksmomenten (G1 tot en met G4) door de les heen.

## Voor de les

**De dag ervoor (dry run)**
- [ ] Volg de checklist in `dry-run.md` en noteer de uitkomsten.
- [ ] Maak je demovoicemail met `demo-script.md` (ongeveer 15 minuten).

**Een uur voor de les**
- [ ] Zet de Colab-link (zie README) op de eerste slide, met een QR-code.
- [ ] Print `handout/handout.html` dubbelzijdig, één per student: voorkant tijdlijn en spelregels, achterkant het scammer-werkblad. Open hem in Chrome en kies *Afdrukken* (A4, schaal 100%, achtergrondafbeeldingen aan).
- [ ] Test de audio van de beamer met je demovoicemail.

## Minuut voor minuut

### 0:00–0:15 Hook
- **0:00** "Open de link op het scherm en start meteen cel 1, die duurt een paar minuten."
- **0:02** "Voor we beginnen: ik kreeg vanochtend een spraakbericht..." Speel je demovoicemail af (`demo-script.md`), zonder iets te zeggen over AI.
- **0:04** Onthulling: "Dat heb ik nooit ingesproken. Dat was een model, gevoed met 10 seconden van mijn stem, gemaakt op een gratis computer van Google." Vraag: "Wie had het door? Hand omhoog."
- **0:06** De nieuwszaken (slides 5–7): INTERPOL-campagne (18 okt), de Britse AI-scam-watchlist (19 okt), de Californische moeder die $5.400 verloor aan een nep-ontvoeringsgesprek met de gekloonde stem van haar dochter (7 okt).
- **0:13** Kijk rond: staat cel 1 overal te draaien?

### 0:15–0:20 Toestemming
- Laat iedereen stap 2 lezen en de vier vinkjes zetten. Benadruk: alleen je eigen stem, niets delen, alles wordt gewist, niet meedoen mag altijd.
- **Opt-out:** wie niet wil opnemen of geen Google-account wil gebruiken, doet mee als luisteraar bij de partner (stap 5) en in alle gesprekken.
- Loop rond: staat er in cel 1 onderaan "✅ Alles werkt"?
  - **❌ Geen GPU:** *Runtime → Runtimetype wijzigen → T4 GPU* en cel 1 opnieuw. Lukt het niet, dan werkt het paar samen op één laptop: eerst de ene stem tot en met stap 5, daarna neemt de ander opnieuw op vanaf stap 3a (de opnames worden overschreven).

### 0:20–0:45 Opnemen en experiment
- **3a leestekst:** de browser vraagt microfoontoegang. Tip: stille hoek, laptop dichtbij, normaal tempo.
- **3b testzin:** één keer de zin voorlezen. Dit wordt de echte clip in de quiz van stap 5.
- **4 experiment:** 12 klonen, een paar minuten op een T4. Laat ze de generatietijd en de realtime-factor bekijken: "Hoe lang duurt het om iemand te laten zeggen wat je wilt?"

**G1, terwijl het model rekent (5 min): het 10-secondenplafond**
- Vraag: "Chatterbox gebruikt maximaal 10 seconden van je stem. Hoeveel clips van 10 seconden van jou staan er online?"
- Laat ze echt tellen: Instagram- en TikTok-stories, YouTube, de begroeting van hun voicemail, opgenomen colleges, spraakberichten in groepsapps.
- Stuur naar: je stem is geen geheim meer. Wie een paar seconden van je heeft, heeft genoeg.

### 0:45–0:55 Echt of nep? (stap 5)
- "Draai je laptop naar je partner. Die luistert naar vier clips (je echte testzin en drie klonen, door elkaar en even hard) en kiest welke echt is. Daarna wisselen."
- Klassikaal turven met handen: "Wie werd voor de gek gehouden? Door welke kloon: 3, 6 of 10 seconden?"
- **Ruis als verraad:** de echte opname bevat kamergeluid, de kloon soms niet. Dat is een hint, geen bewijs: een oplichter voegt zo ruis toe, en over de telefoon valt het weg.

### 0:55–1:20 Denk als een oplichter
- **0:55 Vrije modus (stap 6), 10 min:** laat ze spelen met de schuifjes. Teksten over geld, codes of ontvoering worden geweigerd.
- **1:05 G2, het scammer-werkblad (10 min), op papier:** elk paar bedenkt een voice-scam, maar maakt hem **niet**. Het werkblad vraagt:
  1. Wie is het slachtoffer?
  2. Wiens stem gebruik je, en waar haal je die vandaan?
  3. Welk kanaal: telefoon, spraakbericht, videogesprek?
  4. Wat vraag je: geld, een code, gegevens?
  5. Hoe zet je druk: tijd, emotie, geheimhouding?
  6. Wat zou het slachtoffer laten twijfelen?
- **1:15 Delen (5 min):** twee paren lezen hun scenario voor. Vraag de klas: "Wat maakt dit overtuigend? Wat zou het breken?" Schrijf de antwoorden op het bord; je gebruikt ze in G4.
- Stuur naar: de stem is maar één onderdeel. Druk, haast en een geloofwaardig verhaal doen het echte werk, en vraag 6 is waar de verdediging zit.

### 1:20–1:30 Pauze
Experimenten die nog lopen, lopen gewoon door.

### 1:30–1:55 Kun je het detecteren? (stap 7)
- Laat iedereen stap 7 draaien en de samenvatting bekijken.
- Verwachting (controleer in de dry run, `dry-run.md`):
  - **Watermerk:** ongeveer 1,0 op klonen en 0,0 op echte clips, en het overleeft MP3. Na de telefoonlijn was het in de test van 20 oktober weg (0,02).
  - **Classifier:** herkende in die test de klonen, maar na de telefoonlijn noemde hij alles "echt". Verwacht ook fouten op echte stemmen: hij is getraind op oudere deepfakes.

**G3 (10 min): detectie en de wet**
- "Precies het kanaal dat oplichters gebruiken, de telefoon, schakelt beide detectoren uit. Wat betekent dat?"
- "Het watermerk werkt alleen omdat Resemble AI het erin stopt. Wat als de oplichter een ander open model gebruikt?"
- "Artikel 50 van de AI Act verplicht dat deepfakes gelabeld zijn en dat synthetische audio machinaal herkenbaar is. Wat doet een label in een live telefoongesprek?"

### 1:55–2:20 G4: het grote gesprek
1. **Verantwoordelijkheid:** je stem staat online. Wie is verantwoordelijk als hij gekloond wordt: het platform, de modelmaker of de oplichter?
2. **Open modellen:** Chatterbox is open source (MIT). De vangrails in dit notebook (alleen je eigen stem, het scamfilter) zijn één regel code. "Had je het scamfilter kunnen weghalen?" (Ja: `BLOCKLIST` in `lab/texts.py`.) Moeten zulke modellen open zijn?
3. **Verdediging:** pak de antwoorden van G2 erbij ("wat zou het breken?"). Waarom verslaat een familiewachtwoord de meeste van deze scams, terwijl de detector dat niet doet?
4. **Afsluiter:** "Wat ga je vanavond anders doen?" Laat drie mensen antwoorden.

### 2:20–2:30 Wissen en meegeven
1. Iedereen draait stap 8, vinkt het vakje aan en klikt *Alles wissen*. Dit verwijdert de opnames en daarna de runtime.
2. Iedereen kiest *Bewerken → Alle uitvoer wissen* en sluit het tabblad zonder op te slaan.
3. Vraag of iemand een kopie in Drive heeft opgeslagen. Zo ja: laat diegene het bestand in Drive verwijderen.
4. **Meegeven:** spreek thuis een familiewachtwoord af voor noodgevallen aan de telefoon.

## Noodplannen

| Probleem | Wat je doet |
| --- | --- |
| Paar krijgt geen GPU | Samen op één laptop: eerst de ene stem tot en met stap 5, daarna de ander vanaf stap 3a. Of de partner doet mee als luisteraar. |
| Installatie breekt | Zet in cel 1 vóór de installatie een regel `%env VCL_FULL_INSTALL=1`, verwijder `/content/.vcl_installed`, draai cel 1, en daarna *Runtime → Sessie opnieuw starten* en cel 1 nogmaals. Duurt langer. |
| Audiospeler blijft leeg | Zet in cel 1 `PLAYER` op `embed`. Let op: de audio staat dan in de uitvoer, dus *Alle uitvoer wissen* is verplicht. |
| Microfoon werkt niet | Andere browser (Chrome), of opnemen op de laptop van de partner. |
| Nederlands klinkt slecht | Probeer in cel 1 `MODEL = "v3"`, of gebruik de Engelse zinnen (EN1, EN2) in het gesprek. |
| Classifier laadt niet | Ga door met alleen het watermerk en het eigen oor. |
| Iedereen loopt achter | Sla de vrije modus over (het werkblad blijft) en begin stap 7 direct na de pauze. |

## De code is zichtbaar en aanpasbaar

De kern van het klonen (stap 4 en 6) en de detectie (stap 7) staat als leesbare Python in het notebook. De rest zit in `lab/`, te openen via het 📁-icoon links; wijzigingen daar werken bij de volgende cel die je uitvoert (`lab/live_edit.py`). Ideeën om studenten te laten proberen:
- In stap 4 `REF_LENGTHS = [1, 2, 3]`: hoe weinig stem is genoeg? Stap 5 schudt dan automatisch die klonen.
- In stap 6 de schuifjes: wat doet CFG met het accent, wat doet temperatuur met de stabiliteit?
- In `audio.py` het telefoonfilter strenger of milder maken (`phone_line`): bij welke instelling overleeft het watermerk?
- In `texts.py` het scamfilter bekijken: hoe makkelijk is het te omzeilen?

Gaat er iets stuk door een aanpassing: *Runtime → Sessie opnieuw starten* en cel 1 opnieuw draaien. Opnames blijven bewaard. De originele code terughalen kan met een nieuwe cel `!git -C /content/voice-clone-lab checkout -- .`

## Wat de tools wel en niet afdwingen

De stappen weigeren te werken zonder toestemming, klonen kan alleen met een referentie die live in stap 3 is opgenomen (gecontroleerd met een hash), en de vrije modus weigert scamachtige tekst. Maar studenten zien en bewerken de code, dus ze kunnen die controles ook weghalen. Het notebook noemt dat bewust niet, zodat het niet afleidt tijdens het werk. Het zijn vangrails, geen sloten. Gebruik dat in G4: als een student met één regel het scamfilter uitzet, wat betekent dat voor "veilige" open modellen?
