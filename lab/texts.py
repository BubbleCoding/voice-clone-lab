"""Fixed texts and Dutch UI strings. Texts are neutral on purpose: no names, money or urgency."""

READING_PASSAGE = (
    "Het is dinsdagochtend en het regent zachtjes in Amsterdam. "
    "Op de fiets naar de hogeschool zie ik de grachten, de bomen en de mensen "
    "die haastig naar hun werk gaan. In de kantine ruikt het naar koffie en "
    "versgebakken brood. Vandaag hebben we een workshop, en ik ben benieuwd "
    "wat we gaan leren."
)

# NL1 is the listening-test sentence: students record it themselves and clone it.
TARGET_ID = "NL1"

SENTENCES = [
    {"id": "NL1", "lang": "nl", "text": "Morgen gaan we met de trein naar Utrecht, want de fietsenstalling bij het station is eindelijk weer open."},
    {"id": "NL2", "lang": "nl", "text": "Ik heb de boodschappen al gedaan, dus je hoeft vanavond alleen nog de afwas te doen."},
    {"id": "EN1", "lang": "en", "text": "The library closes at nine tonight, so I will finish the report at home."},
    {"id": "EN2", "lang": "en", "text": "I think the weather will be better on Saturday, so let's go to the beach then."},
]

# Chatterbox uses at most 6 s (speech encoder) and 10 s (decoder) of a reference.
REF_LENGTHS = (3, 6, 10)

MIN_REFERENCE_SPEECH_S = 12.0
MAX_REFERENCE_RECORDING_S = 30
MAX_TARGET_RECORDING_S = 15
FREE_MODE_MAX_CHARS = 200

CONSENT_STATEMENTS = [
    "Ik gebruik alleen mijn eigen stem.",
    "Ik deel geen klonen buiten deze les.",
    "Ik weet dat mijn opnames tijdens de les in Google Colab worden verwerkt.",
    "Ik weet dat alle opnames aan het einde van de les worden verwijderd.",
]

# Lower-case substrings that free mode refuses. Aimed at scam scripts, not exhaustive.
BLOCKLIST = [
    "geld", "overmaken", "overmaak", "maak over", "iban", "pincode", "pin code", "tikkie",
    "rekening", "betalen", "betaal", "ontvoerd", "ontvoering", "losgeld", "bitcoin",
    "cadeaukaart", "bankpas", "wachtwoord", "inlogcode", "verificatiecode",
    "money", "transfer", "bank", "gift card", "giftcard", "wire", "payment", "pay me",
    "password", "kidnap", "ransom", "account number",
]

FREE_MODE_NOTICE = (
    "Let op: berichten die iemand anders nadoen of om geld, codes of gegevens vragen "
    "zijn niet toegestaan, ook niet als grap."
)


def blocked_terms(text):
    """Return the blocklist terms that occur in text (case-insensitive)."""
    lowered = text.lower()
    return [term for term in BLOCKLIST if term in lowered]


def sentence(sentence_id):
    for s in SENTENCES:
        if s["id"] == sentence_id:
            return s
    raise KeyError(sentence_id)
