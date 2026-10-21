Make a PowerPoint deck (.pptx) for a 150-minute workshop for second-year HBO-ICT students (HvA) called **"Jouw stem, hun scam"**. Students clone their own voice with an open-source AI model in Google Colab, test whether their partner can tell real from fake, try to detect the fakes, and discuss the dark side of voice cloning. All slide text is in **Dutch**; keep it exactly as given below.

**Theme: Dark Tech**
- Pure black background (#000000) on every slide, white text (#FFFFFF), no other colours.
- Minimal text: one statement, question or number per slide. No bullet lists longer than four short items. No paragraphs.
- Big, bold type: a heavy sans-serif (for example Inter Black, Montserrat ExtraBold or Arial Black) for headlines, the same family in a lighter weight for the rest. A monospace font is allowed for code-like details (`8 kHz`, `stap 5`).
- Big, bold images that I add myself. For every slide marked **[BEELD]**, leave a large, clearly labelled empty placeholder (full-bleed or half the slide) with the description as placeholder text, so I know what to drop in.
- No logos, clip art, icons, gradients, shadows or animations. 16:9.
- Put the text after **Notes** in the speaker notes, not on the slide.

---

**1. Titel**
- Headline: **Jouw stem, hun scam**
- Small line underneath: `Open de link. Start meteen cel 1.`
- Small text bottom right: `colab.research.google.com/github/BubbleCoding/voice-clone-lab/blob/main/voice_clone_lab.ipynb`
- [BEELD] Placeholder for a QR code to that link (I make it myself), plus a full-bleed image: a sound wave or a microphone in the dark.
- Notes: Students open the notebook and start the setup cell right away; it takes about 4 minutes.

**2. (no title)**
- Completely black, no text. Placeholder for an audio file that I add: my fake voicemail.
- Notes: "Voor we beginnen: ik kreeg vanochtend een spraakbericht, even luisteren." Play it, then simply carry on for a few seconds.

**3. Onthulling**
- Headline: **Dit heb ik nooit gezegd.**
- Notes: "Dat was een model met 10 seconden van mijn stem, gemaakt op een gratis computer van Google. Wie had het door? Hand omhoog."

**4. Hoe makkelijk**
- Three huge numbers stacked or side by side: **10 seconden** · **1 minuut** · **€0**
- Notes: 10 seconds of voice, under a minute of computing, free.

**5. INTERPOL**
- Headline: **18 oktober 2026**
- Line: `INTERPOL start wereldwijde campagne tegen AI-deepfake-scams`
- [BEELD] News photo or screenshot.
- Notes: Source: interpol.int.

**6. Verenigd Koninkrijk**
- Headline: **19 oktober 2026**
- Line: `Eerste officiële AI-scam-watchlist`
- [BEELD] News photo or screenshot.
- Notes: National Trading Standards. Source: aiinsightsnews.net/ai-scams.

**7. Californië**
- Headline: **$5.400**
- Line: `Een moeder hoort haar "ontvoerde" dochter. Het was een kloon.`
- [BEELD] Full-bleed: a phone screen with an incoming call at night.
- Notes: 7 October 2026. Source: Resemble AI Deepfake Watchlist, 2–8 October 2026.

**8. Vandaag**
- Headline: **Vandaag**
- Four short lines: `Klonen` · `Echt of nep?` · `Denk als een oplichter` · `Kun je het detecteren?`
- Notes: 150 minutes, break at 1:20, we wipe everything together at the end.

**9. Spelregels**
- Headline: **Spelregels**
- Four lines: `Alleen je eigen stem` · `Niets delen` · `Alles wordt gewist` · `Niet meedoen mag altijd`
- Notes: Step 2 in the notebook. Opt-out students join their partner as the listener.

**10. G1: tien seconden**
- Headline: **Hoeveel clips van 10 seconden van jou staan er online?**
- [BEELD] Collage or grid of social-media story frames, blurred.
- Notes: While the model is generating. Let them actually count: stories, YouTube, their voicemail greeting, recorded lectures, voice messages in group chats. Steer towards: your voice is not a secret any more.

**11. Echt of nep?**
- Headline: **Echt of nep?**
- Small line: `stap 5 · draai je laptop naar je partner`
- Notes: Partner picks the real clip out of four. Then switch.

**12. Wie werd gefopt?**
- Three huge labels in a row: **3 s** · **6 s** · **10 s**
- Notes: Count hands per clone length. Room noise is a tell, not proof: a scammer can add noise, and a phone line removes it.

**13. Denk als een oplichter**
- Headline: **Denk als een oplichter**
- Six words in a 2×3 or 3×2 grid: `Slachtoffer` · `Stem` · `Kanaal` · `Vraag` · `Druk` · `Twijfel`
- Bottom line: **Schrijf hem op. Maak hem niet.**
- Notes: The worksheet on the back of the handout, in pairs, 10 minutes. Then two pairs read theirs out: what makes it convincing, what would break it? Write the answers on the board for later.

**14. Pauze**
- Headline: **Pauze**
- Small line: `terug om` followed by an empty space for the time
- [BEELD] Optional full-bleed calm image.

**15. Kun je het detecteren?**
- Headline: **Kun je het detecteren?**
- Two words side by side: `Watermerk` vs `Classifier`
- Notes: Step 7. Both run on the original, after MP3 and after a phone line.

**16. De telefoonlijn**
- Headline: **8 kHz**
- Line: `300–3400 Hz · zo klinkt een telefoongesprek`
- [BEELD] Old phone handset or a narrow-band spectrogram.
- Notes: After the phone line, the watermark (1.00 → 0.01) and the classifier both stop working. The channel scammers use defeats both detectors.

**17. G3: de wet**
- Headline: **AI Act, artikel 50**
- Line: `Deepfakes moeten gelabeld zijn.`
- Question: **Wat doet een label in een live telefoongesprek?**
- Notes: Also ask: the watermark works only because Resemble AI adds it. What if the scammer uses another open model? Source: netinfluencer.com (AI Act and the Digital Omnibus).

**18. G4: verantwoordelijkheid**
- Headline: **Wie is verantwoordelijk?**
- Three words: `Platform` · `Modelmaker` · `Oplichter`
- Notes: Your voice is online. Who is responsible when it's cloned?

**19. G4: open modellen**
- Headline: **Het scamfilter is één regel code.**
- Small line: `Moeten zulke modellen open zijn?`
- [BEELD] Screenshot of the BLOCKLIST in lab/texts.py (I make it myself).
- Notes: Chatterbox is open source (MIT). Could you have removed the filter? Yes. What does that mean for "safe" open models?

**20. G4: verdediging**
- Headline: **Familiewachtwoord**
- Small line: `Waarom wint dit van de detector?`
- Notes: Use the board answers from the scammer worksheet: what would break it? Close with: "Wat ga je vanavond anders doen?"

**21. Thuis**
- Headline: **Spreek vanavond een wachtwoord af.**
- [BEELD] Full-bleed: a family dinner table or a phone on a kitchen table.

**22. Wissen**
- Headline: **Wissen**
- Three lines: `Stap 8` → `Bewerken → Alle uitvoer wissen` → `Tabblad sluiten`
- Notes: Everyone at once. Ask whether anyone saved a copy to Drive; if so, delete it there.
