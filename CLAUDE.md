# transcript-local

Aplicație de transcriere locală a meetingurilor, plus minute făcute cu Claude Code.
Vorbește în română.

## Routing

- Utilizatorul spune „am un transcript neprocesat", „fă minuta", „ce transcripturi am
  de procesat", „minuta pentru meetingul de ...", sau dă calea unui fișier din
  `transcripts/`: folosește skill-ul `minuta` (`.claude/skills/minuta/SKILL.md`).
- Utilizatorul vrea alt format de minută: modifică secțiunea „Formatul minutei" din
  SKILL.md, o singură dată. Nu improviza formatul per minută.
- Utilizatorul e pe Mac și întreabă cum înregistrează: `MAC.md`.
- Probleme de instalare sau folosire: `README.md`, secțiunea „Probleme frecvente".

## Reguli

- Nu modifica și nu șterge nimic din `recordings/` și `transcripts/`, cu excepția
  lui `transcripts/processed.md`.
- Toate fișierele `.md` și `.py` se scriu UTF-8 fără BOM.
- Nu inventa conținut în minute: doar ce e în transcript, restul `[neclar]`.
