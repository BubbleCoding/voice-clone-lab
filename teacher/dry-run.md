# Dry run (woensdag 21 oktober)

Na de dry run wordt er niets nieuws meer gebouwd. Noteer bij elk punt wat er gebeurde.

| # | Check | Hoe | Uitkomst |
| --- | --- | --- | --- |
| 1 | Setup op een verse gratis runtime, onder 5 min | Open de Colab-link in een incognitovenster, draai cel 1, noteer de tijd die hij print. | |
| 2 | Installatie zonder fallback | Staat er in cel 1 "Installatie klaar" en zes keer ✅? | |
| 3 | Audiospeler speelt af | Stap 3a: speelt de terugluister-speler af? Zo niet: `PLAYER = "embed"`. | |
| 4 | Microfoon: zwakke laptop (Chrome), Safari, telefoon | Stap 3a op elk apparaat. | |
| 5 | Nederlands klinkt goed bij 3, 6 en 10 s | Stap 4: luister de tabel af. | |
| 6 | Volledig experiment onder 15 min | Stap 2 tot en met 4 met je eigen stem, met de klok erbij. | |
| 7 | Demovoicemail gemaakt | `demo-script.md`. | |
| 8 | Echt of nep? werkt | Stap 5: spelen alle vier de clips, en laat een klik op een knop zien welke echt was? Voer de cel opnieuw uit: is de volgorde anders? | |
| 9 | Detectie: 20 clips onder 3 min | Stap 7, noteer de tijd die hij print. | |
| 10 | Watermerk na MP3 en telefoonlijn | Stap 7, samenvatting: kolom `watermerk_gem` per versie. | |
| 11 | Wat de classifier goed heeft | Stap 7, samenvatting: kolom `classifier_goed`. | |
| 12 | Wissen | Stap 8: is de runtime weg? Zijn na *Alle uitvoer wissen* alle spelers weg? | |
| 13 | Geen-GPU-fallback | Twee mensen na elkaar op één runtime: na stap 5 neemt de tweede opnieuw op vanaf stap 3a. Krijgt stap 5 de nieuwe stem? | |
| 14 | Versies bevriezen | Voeg op de werkende runtime een cel `!pip freeze` toe, stuur de uitvoer naar de coding agent: die pint `requirements-colab.txt` en tagt de repo `v1.0-dry-run`. | |

## Referentie: lokale test van de agent (20 oktober, MacBook, geen GPU)

Op een Mac (Apple-chip, MPS, 16 GB) is de volledige pijplijn met de echte modellen getest: toestemming, opnemen (browserbytes gesimuleerd met de macOS-stem "Ellen"), experiment, quiz, detectie en wissen. Uitkomsten:

| Onderdeel | Resultaat |
| --- | --- |
| Setupchecks | Alles ✅ behalve GPU (verwacht op een Mac). Chatterbox V3 geladen, testzin met watermerk 1,00. |
| Experiment, 12 klonen | 61 s op MPS. Op een T4 naar verwachting vergelijkbaar of sneller. |
| Detectie, 14 clips × 3 versies | 8 s |
| Watermerk, gemiddeld | Klonen: 1,00 origineel, 1,00 na MP3, **0,02 na de telefoonlijn**. Echte clips: 0,00. |
| Classifier | Klonen origineel en MP3: 12/12 als nep herkend. **Na de telefoonlijn: 0/12**, alles "echt". |
| Wissen | Geen audio meer over; `data/` verwijderd. |

Let op bij het lezen: de "echte" clips in deze test waren zelf macOS-spraak (synthetisch), dus dat de classifier ze "nep" noemde, zegt niets over echte stemmen. Met echte studentenstemmen kan dat anders uitvallen; check het in de dry run.

Wat alleen in Colab te testen is: GPU, installatie op Colab's Python, de microfooncel, de audiospeler, en het verwijderen van de runtime.
