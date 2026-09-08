---
name: minuta
description: Transformă un transcript de meeting din transcripts/ într-o minută structurată în minute/. Folosește când utilizatorul spune „am un transcript neprocesat", „fă minuta", „ce transcripturi am de procesat", „minuta pentru meetingul de ieri", „procesează transcriptul", sau dă calea unui fișier din transcripts/. Nu rulează singur la apariția unui transcript, doar la cerere.
---

# minuta — Transcript → minută structurată

Preia un transcript din `transcripts/` și scrie o minută în `minute/`.
Transcriptul rămâne neatins; se adaugă doar o linie în `transcripts/processed.md`.

Căile sunt relative la folderul aplicației (folderul în care s-a deschis Claude Code).
Toate fișierele se scriu UTF-8 fără BOM. Vorbește în română.

## Pas 1 — Ce e de procesat

1. Listează `transcripts/*.md`, fără `processed.md` și fără fișierele `.raw.md`.
2. Citește `transcripts/processed.md`. Fișierele care nu apar acolo sunt neprocesate.
3. Dacă utilizatorul a dat o cale explicită, procesează doar acel fișier (dacă apare
   deja în index, întreabă dacă vrea minuta refăcută).
4. Nimic nou: spune „niciun transcript neprocesat" și oprește-te.
5. Mai multe fișiere noi: arată lista și întreabă pe care le vrea procesate
   (implicit toate). Apoi procesează-le pe rând.

## Pas 2 — Citirea transcriptului

Citește transcriptul integral. Ține cont de cum arată:

- Produs de un model de transcriere locală: are cuvinte stâlcite, nume scrise greșit,
  replici dublate (aceeași frază la doi vorbitori, la câteva secunde distanță). O dublură
  e o singură replică.
- Vorbitorii sunt cel mult două etichete (persoana care a înregistrat și „Ceilalți")
  sau deloc (înregistrare doar cu microfonul, sau transcript adus din MacWhisper).
  Nu ghici cine a spus ce dincolo de ce arată etichetele.
- Dacă participanții nu reies din transcript, pune o singură întrebare:
  „Cine a participat la meeting?" și continuă cu răspunsul primit.

**Regula hard: nu inventa nimic.** Decizii, termene, cifre, nume, responsabili: doar ce e
spus explicit în transcript. Ce e ambiguu se scrie cu `[neclar]`, nu se completează din
context. O minută cu goluri e mai bună decât una cu lucruri care nu s-au spus.

## Pas 3 — Scrierea minutei

1. Creează folderul `minute/` dacă nu există.
2. Scrie `minute/<nume-transcript>.md` (același nume ca transcriptul, fără `.raw`),
   în formatul de mai jos.
3. Adaugă la finalul lui `transcripts/processed.md` linia:
   `- \`<nume-transcript>.md\` — <data de azi, YYYY-MM-DD> — minute/<nume-transcript>.md`
4. Arată utilizatorului secțiunile „Pe scurt", „Decizii" și „Acțiuni" în conversație și
   întreabă dacă vrea ceva ajustat. Ajustările se fac în fișier, nu se rescrie de la zero.

## Formatul minutei

Secțiunea asta e singurul loc unde se definește formatul. Dacă echipa vrea altă
structură (alte secțiuni, altă ordine, tabel în loc de listă), se modifică aici,
o singură dată, și toate minutele următoare ies la fel.

```markdown
# Minută: <subiectul meetingului, dedus din discuție, 3-8 cuvinte>

**Data:** <din numele transcriptului, YYYY-MM-DD>
**Participanți:** <din transcript sau din răspunsul utilizatorului>
**Sursa:** transcripts/<nume-transcript>.md

## Pe scurt

<2-4 fraze: despre ce a fost meetingul și cu ce s-a terminat.>

## Subiecte discutate

- <un bullet per subiect, 1-2 fraze fiecare, în ordinea în care au apărut>

## Decizii

- <doar ce s-a decis explicit; dacă nu s-a decis nimic: „Nicio decizie explicită.">

## Acțiuni

| Ce | Cine | Până când |
|----|------|-----------|
| <acțiunea> | <numele, sau [neclar]> | <termenul spus, sau [neclar]> |

## Întrebări rămase deschise

- <ce s-a ridicat și nu s-a închis; dacă nu există: „Niciuna.">
```

Reguli de stil: propoziții scurte, fără jargon, fără emoji. Citatele din transcript se
pun doar dacă exprimă exact o decizie sau o poziție, cu timestamp `[HH:MM:SS]`.

## Ce NU face skill-ul

- Nu modifică și nu șterge transcripturi sau înregistrări.
- Nu trimite nimic nicăieri (email, chat). Minuta rămâne un fișier local; utilizatorul
  decide unde o duce.
- Nu rezumă mai multe meetinguri într-o singură minută.
