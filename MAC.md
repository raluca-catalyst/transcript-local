# Mac: cum înregistrezi și transcrii

Aplicația din acest repo înregistrează doar pe Windows: sunetul de sistem (ce spun
ceilalți în Meet, Zoom, Teams) se prinde printr-un mecanism care nu există pe Mac.
Pe Mac ai două variante. Minuta se face la fel în ambele, cu Claude Code și skill-ul
`minuta` din repo (vezi [README.md](README.md), secțiunea „Minuta cu Claude Code").

| | Varianta A: MacWhisper Pro | Varianta B: construită cu Claude Code |
|---|---|---|
| Cost | €59, o singură dată | Gratuit |
| Instalare | 10 minute, fără cod | 30-60 de minute, ghidat de Claude Code |
| Sunetul de sistem | Nativ, fără configurări de audio | Prin driverul BlackHole, cu configurare manuală de audio |
| Separare de vorbitori | Da, per persoană | Doar tu vs. ceilalți |
| Recomandată pentru | Oricine vrea să meargă din prima | Cine nu vrea să plătească sau vrea același tool ca pe Windows |

Recomandarea: **Varianta A**. Varianta B rămâne pentru cine are chef de construit.

---

## Varianta A: MacWhisper Pro

MacWhisper e o aplicație de Mac care transcrie local cu aceleași modele Whisper ca
aplicația de Windows. Versiunea gratuită transcrie doar fișiere, cu modele mici.
**Înregistrarea meetingurilor (sunetul de sistem) e în versiunea Pro.**

**Preț:** €59, plată unică, de pe Gumroad (goodsnooze.gumroad.com/l/macwhisper).
Versiunea din App Store e cu abonament lunar și iese mai scump; ia-o pe cea de pe Gumroad.

Denumirile exacte din meniuri pot diferi puțin între versiuni; pașii rămân aceiași.

1. **Cumpără și instalează** MacWhisper Pro de pe Gumroad. Deschide aplicația și
   introdu cheia de licență primită pe email.
2. **Descarcă modelul.** Din setările aplicației, la modele, alege **Large v3 Turbo**
   (sau cel mai mare model pe care îl duce laptopul). Merge bine pe română. Se descarcă
   o singură dată, ~1,5 GB.
3. **La meeting, pornește înregistrarea** cu sunetul de sistem și microfonul.
   MacWhisper detectează singur meetingurile din Zoom, Meet și Teams și propune
   înregistrarea; poți și porni manual din meniul de înregistrare. La prima folosire,
   macOS cere permisiuni pentru microfon și pentru înregistrarea sunetului de sistem:
   acceptă-le.
4. **La final, oprește** înregistrarea. MacWhisper transcrie pe loc, local. Exportă
   transcriptul ca **text sau Markdown** în folderul `transcripts/` al acestui repo,
   cu numele în formatul `AAAA-LL-ZZ-HHMM.md` (de exemplu `2026-09-08-1400.md`), ca să
   se potrivească cu ce așteaptă skill-ul de minute.
5. **Minuta.** Deschide un terminal în folderul repo-ului, scrie `claude`, apoi
   „am un transcript neprocesat". Restul e ca pe Windows.

Ce ai nevoie din acest repo pe Mac, în Varianta A: doar folderul descărcat (pentru
skill-ul `minuta` și `transcripts/`). Nu rulezi `setup.ps1`, nu instalezi Python.

---

## Varianta B: construită cu Claude Code (gratuit)

Aplicația e gândită ca partea de Mac să fie construită de Claude Code pe loc, în
folderul repo-ului. Tu instalezi trei lucruri, apoi copiezi blocul de instrucțiuni de
mai jos în Claude Code și el face restul, întrebându-te când are nevoie de tine.

**Înainte de a porni:**

- **Python 3.10 sau mai nou** (`python3 --version` în Terminal; dacă lipsește,
  instalează de pe python.org sau cu `brew install python`).
- **Claude Code** instalat și logat.
- **BlackHole 2ch**, driverul audio virtual gratuit prin care se prinde sunetul de
  sistem: `brew install blackhole-2ch` sau instalatorul de pe existential.audio/blackhole.
  Îți cere restart sau parola de administrator.

**Apoi:** deschide Terminal în folderul repo-ului, scrie `claude`, și copiază în
conversație tot blocul de mai jos, ca prim mesaj.

---

Construiește partea de macOS a acestei aplicații de transcriere locală. Vorbește-mi în
română. Citește întâi `README.md`, `meet.py` și `capture.py` ca să înțelegi ce există.

## Ce trebuie să faci

1. **Scrie `capture_mac.py`**, cu exact aceeași interfață ca `capture.py` (varianta de
   Windows), ca `meet.py` să meargă neschimbat:
   - clasa `DualRecorder(mic_path, system_path)`: pornește la construcție două
     înregistrări simultane în fișiere WAV int16 (microfonul și sunetul de sistem),
     are metoda `stop()`; dacă a doua înregistrare eșuează, o închide curat pe prima;
   - clasa `MicRecorder(mic_path)`: doar microfonul, cu `stop()`;
   - folosește biblioteca `sounddevice` (stream de input cu callback, scris continuu
     într-un WAV, cu lock ca să nu scrii după închidere), la rata nativă a fiecărui
     dispozitiv;
   - canalul „microfon" e dispozitivul de input default din macOS;
   - canalul „sistem" e dispozitivul de input numit **BlackHole** (caută-l după nume în
     lista de dispozitive); dacă nu există, ridică o eroare clară în română, care spune
     că trebuie instalat BlackHole 2ch și trimite la pasul de configurare de mai jos;
   - mesaje clare de eroare în română pentru: fără microfon default, fără BlackHole,
     permisiune de microfon refuzată.
2. **Adaugă `sounddevice` în `requirements.txt`** cu marker de platformă
   (`sounddevice; sys_platform == "darwin"`), fără să atingi liniile existente.
3. **Scrie `setup.sh`** (echivalentul lui `setup.ps1`): creează un virtualenv `.venv`
   în folderul repo-ului, instalează `requirements.txt` în el, creează folderele
   `recordings/`, `transcripts/`, `minute/`, și scrie la final exact ce comandă
   folosesc ca să pornesc un meeting (`.venv/bin/python meet.py`).
4. **Ghidează-mă prin configurarea audio din macOS**, pas cu pas, așteptând confirmarea
   mea după fiecare pas, pentru ca sunetul meetingului să ajungă și în BlackHole și în
   căștile/boxele mele:
   - în aplicația **Audio MIDI Setup** (din Applications > Utilities), creez un
     **Multi-Output Device** care conține ieșirea mea obișnuită (boxe sau căști) și
     BlackHole 2ch;
   - setez acest Multi-Output Device ca ieșire de sunet a sistemului (System Settings >
     Sound > Output) pe durata meetingurilor;
   - microfonul rămâne cel obișnuit, ca input default;
   - explică-mi și cum revin la ieșirea normală după meeting.
5. **Testează cu mine**: rulează `.venv/bin/python meet.py`, pune-mă să pornesc un video
   pe YouTube și să vorbesc 20 de secunde, apoi oprim cu Ctrl+C și verificăm împreună că
   transcriptul din `transcripts/` are replici sub ambele etichete.
6. Dacă vreau doar întâlniri fizice, fără BlackHole: confirmă că `python meet.py --mic`
   merge fără configurarea audio de mai sus.

## Cum lucrezi

- Explică-mi planul pe scurt înainte să scrii cod, apoi construiește fișier cu fișier.
- Nu modifica `capture.py`, `meet.py`, `merge.py`, `cleanup.py`, `transcribe.py`: partea
  comună e testată și trebuie să rămână identică pe Windows și Mac.
- Cod scurt, comentarii în română, fără alte dependențe în afară de `sounddevice`.
- Fișierele `.py` și `.md` se scriu UTF-8 fără BOM.
- La final, adaugă în `README.md`, sub secțiunea „Folosire", un paragraf scurt „Pe Mac"
  cu comanda de pornire și reamintirea de a comuta ieșirea audio pe Multi-Output Device.

---

Când Claude Code a terminat, folosirea e ca pe Windows: pornești înainte de meeting,
oprești cu Ctrl+C, transcriptul apare în `transcripts/`, minuta se face cu „am un
transcript neprocesat".

**Limită cunoscută a Variantei B:** trebuie să comuți ieșirea audio pe Multi-Output
Device înainte de fiecare meeting (și înapoi după), altfel canalul „Ceilalți" iese gol.
Varianta A n-are problema asta.
