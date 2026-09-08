"""Curățare transcript cu Claude Code headless (`claude -p`)."""
import shutil
import subprocess

from config import MY_LABEL, OTHERS_LABEL

CHUNK_MAX_LINES = 120
TIMEOUT_SECONDS = 300

_PROMPT_TEMPLATE = """Primești o bucată dintr-un transcript de meeting în română (posibil cu \
pasaje în engleză), produs de un model de transcriere locală. Curăț-o astfel:
- Corectează cuvintele stâlcite DOAR când corecția e evidentă din context.
- Pune diacritice corecte.
- Elimină replicile care sunt dubluri/ecou al unei replici vecine (același \
conținut, ușor stâlcit, la câteva secunde distanță) — păstreaz-o pe cea curată.
- Atribuirea vorbitorului la dubluri: înregistrarea are două canale — \
microfonul (etichetat {me}) și sunetul de sistem (etichetat {others}). \
Canalul de sistem NU poate conține vocea persoanei {me}, dar microfonul poate prinde \
boxele. REGULĂ STRICTĂ, aplic-o mecanic la fiecare pereche de replici vecine \
(sub ~15 secunde distanță) cu conținut comun sub ambele etichete:
  1. Textul comun aparține întotdeauna lui **{others}**. Păstrează-l DOAR în \
replica {others} (alege varianta mai coerentă dintre cele două ca formulare).
  2. Șterge textul comun din replica {me}. Dacă în replica {me} rămân și \
vorbe proprii (care nu apar sub {others}), păstrează doar acele vorbe sub \
{me}; dacă nu rămâne nimic, șterge complet replica {me}.
  3. Nu șterge niciodată replica {others} în favoarea celei {me} și nu \
muta conținut comun sub eticheta {me}, indiferent care variantă sună mai \
curat — varianta mai curată se folosește doar ca text în replica {others}.
Exemplu — intrare:
**[00:10:02] {me}:** Sigur că da. Am terminat raportul aseară târziu.
**[00:10:05] {others}:** Am terminat raportul aseară târziu, abia am dormit.
Ieșire corectă:
**[00:10:02] {me}:** Sigur că da.
**[00:10:05] {others}:** Am terminat raportul aseară târziu, abia am dormit.
- NU inventa conținut, NU parafraza, NU rezuma. Ce nu poți corecta cu \
încredere lasă exact cum e sau marchează cu [neclar].
- Păstrează intacte timestamps-urile [HH:MM:SS], etichetele de vorbitor și \
formatarea markdown (**[...] Nume:**).
Răspunde DOAR cu textul curățat, fără comentarii."""

PROMPT = _PROMPT_TEMPLATE.format(me=MY_LABEL, others=OTHERS_LABEL)

# Varianta pentru înregistrări cu un singur canal (întâlnire fizică, doar
# microfon): fără etichete de vorbitor. Fără regulile de atribuire —
# aplicate pe un transcript neetichetat, ele INVENTEAZĂ atribuirea.
PROMPT_SINGLE = """Primești o bucată dintr-un transcript de meeting în română \
(posibil cu pasaje în engleză), produs de un model de transcriere locală, \
dintr-o înregistrare cu un singur canal, fără vorbitori identificați. Curăț-o \
astfel:
- Corectează cuvintele stâlcite DOAR când corecția e evidentă din context.
- Pune diacritice corecte.
- NU inventa conținut, NU parafraza, NU rezuma. Ce nu poți corecta cu \
încredere lasă exact cum e sau marchează cu [neclar].
- Păstrează intacte timestamps-urile [HH:MM:SS] și formatarea markdown \
(**[...]** text). Replicile NU au etichete de vorbitor — NU adăuga nume sau \
etichete de vorbitor sub nicio formă.
Răspunde DOAR cu textul curățat, fără comentarii."""


class CleanupError(Exception):
    pass


def _chunk_lines(lines, max_lines=CHUNK_MAX_LINES):
    """Împarte liniile în bucăți de ~max_lines, tăind doar la linii goale."""
    chunks = []
    current = []
    for line in lines:
        current.append(line)
        if len(current) >= max_lines and line == "":
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def _run_claude(prompt, chunk_text):
    exe = shutil.which("claude")
    if not exe:
        raise CleanupError("nu găsesc comanda `claude` în PATH")
    # --strict-mcp-config + --setting-sources "" = pornire minimă (fără MCP
    # servers, plugin-uri sau skill-uri) — curățarea de text nu are nevoie de
    # ele, iar config-ul complet face pornirea lentă.
    # --effort low = fără extended thinking; task mecanic, mult mai rapid.
    result = subprocess.run(
        [
            exe,
            "-p",
            prompt,
            "--model",
            "sonnet",
            "--output-format",
            "text",
            "--strict-mcp-config",
            "--setting-sources",
            "",
            "--effort",
            "low",
        ],
        input=chunk_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise CleanupError(f"claude a eșuat: {result.stderr.strip()[:200]}")
    out = result.stdout.strip()
    if not out:
        raise CleanupError("claude a întors răspuns gol")
    return out


def clean_transcript(md_text, run=None, single_channel=False):
    """Curăță transcriptul bucată cu bucată, cu un retry per bucată.

    Cu single_channel=True (înregistrare doar cu microfonul) se folosește
    PROMPT_SINGLE — fără regulile de atribuire, ca să nu se inventeze
    etichete de vorbitor pe replici neetichetate.

    O bucată care eșuează de două ori rămâne necurățată (text brut) și
    procesarea continuă. Ridică CleanupError doar dacă TOATE bucățile au
    eșuat — atunci apelantul cade pe transcriptul brut întreg.
    """
    run = run or _run_claude
    prompt = PROMPT_SINGLE if single_channel else PROMPT
    lines = md_text.splitlines()
    # Titlul ("# Meeting <stamp>") nu intră în curățare: Claude îl poate
    # rescrie sau șterge, iar pierderea lui e nedeterministă. Îl scoatem și îl
    # punem la loc verbatim.
    title = None
    if lines and lines[0].startswith("# "):
        title = lines[0]
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    cleaned_chunks = []
    total = 0
    failed = 0
    for chunk in _chunk_lines(lines):
        chunk_text = "\n".join(chunk)
        if not chunk_text.strip():
            continue
        total += 1
        cleaned = None
        for _attempt in range(2):
            try:
                cleaned = run(prompt, chunk_text).rstrip()
                break
            except Exception:
                continue
        if cleaned is None:
            failed += 1
            cleaned = chunk_text.rstrip()
        cleaned_chunks.append(cleaned)
    if total and failed == total:
        raise CleanupError("claude a eșuat pe toate bucățile")
    if failed:
        print(
            f"Atenție: {failed} bucăți din {total} au rămas necurățate "
            "(claude a eșuat pe ele)."
        )
    body = "\n\n".join(cleaned_chunks).rstrip()
    if title is not None:
        body = f"{title}\n\n{body}".rstrip()
    return body + "\n"
