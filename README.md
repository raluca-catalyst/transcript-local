# transcript-local

Înregistrezi meetingul, primești transcriptul ca fișier text, apoi îi ceri lui Claude
minuta. Totul se întâmplă pe laptopul tău: audio-ul și transcriptul nu pleacă nicăieri,
nu ai nevoie de cont, nu plătești nimic în plus.

Merge pe **Windows** (aplicația din acest repo) și pe **Mac** (vezi [MAC.md](MAC.md)).
Partea de minute e la fel pe amândouă.

## Ce face

1. **Înregistrează** meetingul de pe Meet, Zoom sau Teams: microfonul tău și sunetul
   care iese din laptop (ceilalți). Participanții nu văd nimic, nu intră niciun bot în call.
2. **Transcrie** local, în română sau engleză, cu timestamps și două etichete de vorbitor:
   tu și ceilalți.
3. **Curăță** transcriptul cu Claude (diacritice, cuvinte stâlcite, ecouri).
4. **Minuta** o face Claude Code, din transcript, cu skill-ul `minuta` inclus în repo.

## Ce ai nevoie (Windows)

- **Windows 10 sau 11.**
- **Python 3.10 sau mai nou.** Descarcă de pe [python.org/downloads](https://www.python.org/downloads/).
  La instalare, bifează obligatoriu **„Add python.exe to PATH"** (căsuța de jos din primul ecran).
- **Claude Code** instalat și logat (comanda `claude` trebuie să meargă într-un terminal).
  Fără el, aplicația merge tot, dar transcriptul rămâne necurățat și minutele nu se pot face.
- ~2 GB liberi pe disc pentru modelul de transcriere.

## Instalare (Windows, o singură dată)

1. **Descarcă aplicația.** Pe pagina repo-ului, butonul verde **Code**, apoi **Download ZIP**.
   Dezarhivează folderul undeva stabil, de exemplu în `Documents\transcript-local`.
   (Dacă ai `git`, poți și `git clone`.)
2. **Rulează setup-ul.** Deschide folderul, click dreapta pe `setup.ps1`, apoi
   **Run with PowerShell**. Dacă Windows întreabă de permisiuni, acceptă.
   Sau, dintr-un terminal deschis în folder:

   ```
   powershell -ExecutionPolicy Bypass -File setup.ps1
   ```

   Setup-ul instalează dependențele, creează folderele și pune pe Desktop shortcut-ul
   **„Transcript meeting"**.
3. **Scrie-ți numele.** Deschide `config.py` cu Notepad și înlocuiește `"Eu"` cu numele tău,
   de exemplu `"Alexandra"`. Așa apari în transcript.
4. **Prima rulare.** Prima transcriere descarcă modelul (~1,6 GB), deci durează mai mult.
   Ai nevoie de internet doar atunci.

## Folosire

**Meeting online (Meet, Zoom, Teams):**

1. Înainte de meeting, dublu-click pe **„Transcript meeting"** de pe Desktop.
   Se deschide o fereastră neagră care scrie „Înregistrez".
2. Ține fereastra deschisă pe durata meetingului. Căștile sunt ok.
3. La final, click în fereastră și apasă **Ctrl+C**. Transcrierea pornește singură.
   Durează 10-20 de minute pentru o oră de meeting. Fereastra rămâne deschisă și îți
   arată unde e transcriptul.

**Întâlnire fizică (doar microfonul, prinde toată sala):**

Dintr-un terminal deschis în folderul aplicației:

```
python meet.py --mic
```

Aici transcriptul nu are etichete de vorbitor.

**Unde ajung fișierele:**

| Ce | Unde |
|----|------|
| Audio-ul brut | `recordings\AAAA-LL-ZZ-HHMM-mic.wav` și `-system.wav` |
| Transcriptul curățat | `transcripts\AAAA-LL-ZZ-HHMM.md` |
| Transcriptul necurățat | `transcripts\AAAA-LL-ZZ-HHMM.raw.md` |
| Minuta | `minute\AAAA-LL-ZZ-HHMM.md` |

Două meetinguri în același minut nu se suprascriu (primesc sufix `-2`, `-3`).
Audio-ul rămâne pe disc: dacă transcrierea crapă, nimic nu e pierdut.

**Re-transcriere** (dacă transcrierea a crăpat sau ai închis fereastra prea devreme):

```
python meet.py recordings\2026-09-08-1400-mic.wav recordings\2026-09-08-1400-system.wav
```

**Un fișier audio de oriunde** (telefon, alt recorder): `python meet.py cale\catre\fisier.m4a`.

## Minuta cu Claude Code

Repo-ul vine cu un skill de Claude Code numit `minuta`. Nu trebuie instalat separat:
Claude Code îl vede automat când e deschis în folderul aplicației.

1. Deschide un terminal în folderul aplicației (click dreapta în folder, **Open in Terminal**).
2. Scrie `claude` și apasă Enter.
3. Spune-i: **„am un transcript neprocesat"** sau **„fă minuta pentru meetingul de azi"**.

Claude găsește transcripturile care n-au încă minută, citește transcriptul, scrie minuta în
`minute\` și îți arată pe scurt deciziile și acțiunile. Minuta are: pe scurt, subiecte
discutate, decizii, acțiuni (ce / cine / până când), întrebări deschise.

**Regula skill-ului:** nu inventează nimic. Ce nu s-a spus explicit în meeting apare ca
`[neclar]`, nu se completează din context.

**Vrei alt format de minută?** Spune-i lui Claude, în același folder: „schimbă formatul
minutei: vreau și o secțiune de riscuri" (sau ce ai nevoie). Formatul stă într-un singur
loc, în `.claude\skills\minuta\SKILL.md`, secțiunea „Formatul minutei", și toate minutele
următoare ies la fel.

## Limite asumate

- Vorbitorii sunt doar **tu vs. ceilalți** (pe canale audio), nu per persoană.
- La întâlnirile fizice nu există separare de vorbitori.
- Transcrierea e bună, nu perfectă: numele proprii și termenii tehnici pot ieși stâlciți.
  De asta transcriptul se curăță cu Claude, iar minuta marchează ce e neclar.
- Curățarea cu Claude folosește abonamentul tău de Claude Code. Dacă `claude` nu e
  instalat, transcriptul final e identic cu cel brut, iar fereastra anunță asta.

## Probleme frecvente

**„python is not recognized"** la setup. Python nu e în PATH. Reinstalează Python cu
căsuța „Add python.exe to PATH" bifată, apoi rulează din nou setup-ul.

**„Nu am găsit dispozitivul de loopback pentru difuzoare."** Windows n-are un dispozitiv
de ieșire audio setat ca default. Setări > Sistem > Sunet > alege ieșirea (boxe sau
căști), apoi pornește din nou.

**Canalul „Ceilalți" iese gol.** Ai avut sunetul meetingului pe alt dispozitiv decât cel
default din Windows (de exemplu căști Bluetooth conectate după ce ai pornit
înregistrarea). Pornește înregistrarea după ce ai conectat căștile.

**„Curățarea Claude a eșuat".** Comanda `claude` nu e instalată sau nu ești logat.
Transcriptul brut e salvat oricum; poți rula curățarea mai târziu, retranscriind din
`recordings\`.

**Prima transcriere durează foarte mult.** Se descarcă modelul (~1,6 GB). Doar prima dată.

## Cum e făcută (pentru cine vrea să modifice)

| Fișier | Rol |
|--------|-----|
| `meet.py` | Punctul de intrare: înregistrare, transcriere, salvare |
| `capture.py` | Înregistrarea celor două canale pe Windows (WASAPI loopback) |
| `transcribe.py` | Transcrierea cu faster-whisper, modelul large-v3-turbo, pe CPU |
| `merge.py` | Împletirea celor două canale, eliminarea ecoului |
| `cleanup.py` | Curățarea cu `claude -p`, bucată cu bucată |
| `config.py` | Numele tău și eticheta pentru ceilalți |
| `.claude/skills/minuta/` | Skill-ul de minute pentru Claude Code |
| `tests/` | Teste (`python -m pytest`) |

Pentru a modifica ceva, cel mai simplu e să deschizi Claude Code în folder și să-i ceri
schimbarea. Codul e scurt și comentat în română.

Licență MIT. Construită de Raluca Păduraru pentru propriile meetinguri, apoi
generalizată ca să poată fi folosită de oricine.
