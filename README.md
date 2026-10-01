# Kometfrakteratene

Her skal dere lage et CLI med Typer og bruke det til å spille Kometfrakteratene. Funksjonene som snakker med serveren er ferdige. Dere bestemmer kommandoene, inputten og hva brukeren får se.

**Denne README-en er veiledningen. All koden dere skal skrive til spillet hører hjemme i `cli.py`.**

## Kom i gang

Åpne repoet i GitHub Codespaces: **Code → Codespaces → Create codespace**. Kjør dette i terminalen fra root i repoet:

```sh
uv sync --frozen
```

Vi gjør tutorialen sammen i `tutorial/main.py`. Du trenger ikke et eget oppgaveark. Når vi begynner med spillet, gå tilbake til root i repoet og kjør:

```sh
uv run python -m verktoy.oppsett
uv run python cli.py --help
uv run python cli.py status
```

Behold serveradressen som foreslås, `https://orbital-courier.onrender.com`, og bruk koden du får av meg. Oppsettet sjekker at serveren svarer før du registrerer deg. Første gang kan det ta litt tid.

`verktoy/` inneholder det ferdige oppsettet og API-klienten. Du trenger ikke endre noe der. Spillerkontoen lagres i `.player.json`, som ikke skal deles eller legges i Git. Har du allerede registrert deg i dette repoet, kan du bruke den samme kontoen videre.

## Oppgaven

`status` er ferdig i `cli.py`, så du har et eksempel å ta utgangspunkt i. Resten lager du selv. Du velger navn på kommandoene og om input passer best som argument eller option.

1. **Finn et oppdrag.** Lag kommandoer for å se stasjoner og ledige oppdrag. Brukeren må kunne finne ut hva de skal frakte, hvor de skal hente det og hvor det skal leveres.
2. **Gjør en levering.** Legg til reise, lasting og levering. Prøv en hel tur gjennom CLI-et ditt.
3. **Rett opp feil.** Legg til lossing og nullstilling av øvingen. Hvis noen fyller skipet med feil last, skal de kunne komme seg videre. Spør før du nullstiller.
4. **Gjør det lett å bruke.** Skriv hjelpetekst og et eksempel i docstringene. Prøv `--help`, skriv noe feil og se om meldingen faktisk hjelper deg.

Målet er at noen skal kunne bruke kommandoene uten å lese Python-koden din. Etterpå tar vi en uhøytidelig konkurranse :)

Hvis du får tid, kan du f.eks. legge til filtrering av oppdrag, tabeller med Rich eller `--json` på flere kommandoer. Et lite CLI som er lett å forstå er helt fint. Spill én handling om gangen, så du får prøvd hvordan kommandoene fungerer i bruk.

## Hvordan spillet fungerer

Du flyr mellom fem stasjoner og leverer last for å få poeng:

| Stasjon (`id`) | Last du kan hente der |
|---|---|
| Earth (`earth`) | `food`, `water` |
| Luna (`luna`) | `tools` |
| Mars (`mars`) | `medicine` |
| Europa (`europa`) | `fuel` |
| Titan (`titan`) | `parts` |

En levering består av å finne et oppdrag, fly til hentestedet, laste riktig mengde, fly til mottakeren og levere oppdraget. Bruk ID-ene i tabellen når du kaller funksjonene.

- Skipet har plass til **6 enheter totalt**, på tvers av alle typer last.
- Du kan fly direkte mellom alle stasjonene. Det koster ingenting å reise, og det er nok varer til alle.
- Hver levering gir **10 poeng**. Det er 12 oppdrag per runde, og hvert oppdrag kan leveres én gang.
- Du har dine egne oppdrag og din egen last. Ingen andre kan ta dem fra deg.
- Lossing kaster last uten å gi poeng. Du kan losse på alle stasjoner.
- I øvingsrunden kan du nullstille posisjon, last og poeng. Kontoen din beholdes. I konkurransen er nullstilling stengt.
- Konkurransen starter med en ny runde. Oppdrags-ID-er og mengder endrer seg, så les det aktuelle oppdraget.
- Hvis runden er satt på pause eller ferdig, kan du fortsatt se status og oppdrag, men ikke gjøre flere spillhandlinger.

## Python-funksjonene du har tilgjengelig

`cli.py` importerer `GameClient` og `GameError` for deg. Inne i en kommando lager du klienten og kaller en av funksjonene:

```python
game = GameClient.from_config()
data = game.list_contracts(status="open")
for contract in data["contracts"]:
    print(contract["id"], contract["item"], contract["quantity"])
```

Alle funksjonene returnerer vanlige Python-dicts. Du trenger ikke skrive HTTP-kall eller bruke async.

| Kall | Hva du får tilbake / hva som skjer |
|---|---|
| `game.status()` | Status med `name`, `location`, `cargo`, `score`, `completed`, `mode`, `capacity` og `supplies_here`. |
| `game.map()` | `data["stations"]`, en liste med stasjoner. Hver har `id`, `name` og `supplies`. |
| `game.list_contracts(status="open")` | `data["contracts"]`, en liste med oppdrag. Filteret kan være `all`, `open` eller `completed`. |
| `game.get_contract("P01")` | Ett oppdrag, direkte som en dict. Se eksemplet under. |
| `game.travel("luna")` | Flytter skipet og returnerer oppdatert spillerstatus. |
| `game.load_cargo("food", quantity=2)` | Laster varer fra stasjonen du er på. Returnerer spillerstatus. |
| `game.unload_cargo("food", quantity=1)` | Kaster last fra skipet. Returnerer spillerstatus. |
| `game.deliver("P01")` | Leverer oppdraget hvis du er på riktig sted med riktig last. Returnerer spillerstatus. |
| `game.reset_practice()` | Nullstiller øvingen og returnerer spillerstatus. |
| `game.session()` | Rundens `mode` og `seconds_remaining`. |
| `game.rename("Nytt navn")` | Endrer navnet i øvingsrunden. Returnerer `name`. |

Et oppdrag ser slik ut:

```python
{
    "id": "P01",
    "item": "food",
    "source": "earth",
    "destination": "luna",
    "quantity": 2,
    "reward": 10,
    "completed": False,
}
```

For dette oppdraget må du altså hente 2 `food` på `earth`, reise til `luna` og kalle `deliver("P01")`. Bruk verdiene fra oppdraget du har hentet, ikke hardkod dette eksemplet i kommandoene.

`cargo` er en dict med antall per vare, f.eks. `{"food": 2, "water": 1}`. `completed` er en liste med ferdige oppdrags-ID-er. For et kart kan du gå gjennom `data["stations"]` og vise `station["name"]` sammen med `", ".join(station["supplies"])`.

Hvis du vil se hele API-et, finnes det på [serverens dokumentasjonsside](https://orbital-courier.onrender.com/docs). Oversikten over er nok til å lage CLI-et.

## Når noe går galt

Følg `try`/`except`-eksemplet i `status`. Både `GameClient.from_config()` og API-kallet skal være inne i `try`, slik at du også fanger feil med oppsettet.

`GameError` gir deg `message` (hva som gikk galt), `hint` (hva brukeren kan gjøre) og `code` (en fast feilkode). Print feilmeldinger med `file=sys.stderr` og avslutt med `raise typer.Exit(1)`. Behold vanlig output på stdout, særlig når du lager `--json`. La API-kallene ligge inne i kommandoene, så `--help` fungerer uten kontakt med serveren.

- **Fullt skip?** Lever eller loss noe. Husk at grensen er 6 enheter totalt.
- **Feil stasjon eller manglende last?** Sjekk oppdraget og statusen din.
- **Mangler oppsett?** Kjør `uv run python -m verktoy.oppsett`.
- **Mistet token eller fikk feil under registrering?** Si fra, så sjekker vi om du ble registrert. Ikke lag flere kontoer for å prøve igjen.
- **Nettverksfeil?** Sjekk status før du gjentar en handling. Endringen kan ha gått gjennom selv om svaret forsvant. Hvis forbindelsen feiler med en gang, vis meg feilmeldingen.

Vanligvis leses serveradresse og token fra `.player.json`. Hvis du har satt `ORBITAL_URL` eller `ORBITAL_TOKEN`, bruker klienten disse verdiene i stedet.
