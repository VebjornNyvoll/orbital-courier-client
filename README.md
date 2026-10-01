# Kometfrakteratene

Dere skal lage et CLI med Typer og bruke det til å frakte varer mellom romstasjoner. Hver levering gir poeng. Funksjonene som snakker med spillet er ferdige; dere lager kommandoene, hjelpeteksten og det brukeren får se i terminalen.

**Jobb i `cli.py`. Denne README-en inneholder oppgaven, spillereglene og alle spillfunksjonene dere trenger.**

- [Kom i gang](#kom-i-gang)
- [Lag den første kommandoen](#lag-den-forste-kommandoen)
- [Hva lager jeg videre?](#hva-lager-jeg-videre)
- [Spilleregler](#spilleregler)
- [Funksjonsoversikt og returverdier](#funksjonsoversikt)
- [Feilmeldinger og hjelp](#feilmeldinger-og-hjelp)

<a id="kom-i-gang"></a>
## Kom i gang

Åpne repoet i GitHub Codespaces: **Code → Codespaces → Create codespace**. Kjør dette i terminalen fra root i repoet:

```sh
uv sync --frozen
```

Tutorialen gjør vi sammen i `tutorial/main.py`. Når vi begynner med spillet, gå tilbake til root i repoet og kjør:

```sh
uv run python -m verktoy.oppsett
uv run python cli.py status
```

Behold serveradressen som foreslås, og bruk workshop-koden du får av meg. Serveren kan bruke litt tid på å våkne første gang. Har du allerede satt opp en spiller i dette repoet, kan du gå rett til `status`.

Du skal nå se navnet ditt, hvor skipet er, last og poeng. `status` er den eneste spillkommandoen som er ferdig i startfila.

`verktoy/` inneholder de ferdige hjelpefunksjonene. Spillerkontoen lagres i `.player.json`, som Git ignorerer. Du trenger ikke endre disse filene eller håndtere innlogging i kommandoene dine.

<a id="lag-den-forste-kommandoen"></a>
## Lag den første kommandoen

Start med å vise ledige oppdrag. Åpne `cli.py` og legg dette **over** `if __name__ == "__main__":`, ved siden av den eksisterende `status`-kommandoen. Importene du trenger finnes allerede i fila.

```python
@app.command()
def oppdrag():
    """Vis ledige oppdrag med hentested, mottaker og antall varer."""
    try:
        game = GameClient.from_config()
        data = game.list_contracts(status="open")
    except GameError as exc:
        print(f"Feil: {exc.message}\n{exc.hint}", file=sys.stderr)
        raise typer.Exit(1) from None

    if not data["contracts"]:
        print("Ingen ledige oppdrag.")
        return

    for contract in data["contracts"]:
        print(
            f"{contract['id']}: {contract['quantity']} {contract['item']} "
            f"fra {contract['source']} til {contract['destination']}"
        )
```

Kjør i terminalen:

```sh
uv run python cli.py oppdrag
uv run python cli.py oppdrag --help
```

Den første linja i øvingsrunden blir:

```text
P01: 2 food fra earth til luna
```

Hva skjer her?

| Kode | Hva den gjør |
|---|---|
| `@app.command()` | Gjør Python-funksjonen `oppdrag` til en terminalkommando. |
| Docstringen under `def` | Blir hjelpeteksten når du bruker `--help`. |
| `GameClient.from_config()` | Lager en klient med den lagrede serveradressen og spillertokenet ditt. |
| `game.list_contracts(status="open")` | Henter ledige oppdrag. Returnerer en dict med nøkkelen `contracts`. |
| `data["contracts"]` | Lista du går gjennom. Hvert element er en dict med ett oppdrag. |
| `print(...)` | Bestemmer hva brukeren ser. API-funksjonene printer ingenting selv. |

`oppdrag` er altså navnet brukeren skriver i terminalen. `list_contracts` er Python-funksjonen du bruker inne i kommandoen. De trenger ikke hete det samme. Resten av funksjonsoversikten under viser **Python-kall du kan bruke i egne kommandoer**, ikke ferdige terminalkommandoer.

<a id="hva-lager-jeg-videre"></a>
## Hva lager jeg videre?

Få til én levering først. Du velger selv kommandonavn og om input skal være argumenter eller options.

| Steg | Brukeren trenger å kunne … | Python-funksjon |
|---|---|---|
| 1 | Finne et ledig oppdrag | `game.list_contracts(status="open")` |
| 2 | Se hele oppdraget | `game.get_contract(contract_id)` |
| 3 | Fly til hentestedet | `game.travel(destination)` |
| 4 | Laste riktig vare og antall | `game.load_cargo(item, quantity)` |
| 5 | Fly til mottakeren | `game.travel(destination)` |
| 6 | Levere og se poengene | `game.deliver(contract_id)` |

For **P01 i øvingen** er turen: Earth → last 2 `food` → Luna → lever P01. Skipet starter på Earth. Etter leveringen skal `status` vise 10 poeng og P01 som ferdig. Oppdrags-ID-er og mengder endrer seg i konkurransen, så bruk opplysningene fra det aktuelle oppdraget.

Når dette fungerer, legg til kart, lossing og nullstilling av øvingen. Lossing lar brukeren rydde opp hvis de har fylt skipet med feil last. Spør før du nullstiller.

Prøv så å bruke CLI-et gjennom `--help`. Er det tydelig hvilke verdier du kan sende inn? Hva skjer hvis du skriver feil? Får du se hvor du havnet etter en reise, og hvor mange poeng en levering ga?

Hvis du får tid, kan du legge til filtrering, tabeller med Rich, eller `--json`. Hjelpetekst og brukseksempler hører hjemme i kommandoenes docstrings. Etterpå tar vi en uhøytidelig konkurranse :)

<a id="spilleregler"></a>
## Spilleregler

| Stasjon | ID til funksjonene | Varer du kan hente |
|---|---|---|
| Earth | `earth` | `food`, `water` |
| Luna | `luna` | `tools` |
| Mars | `mars` | `medicine` |
| Europa | `europa` | `fuel` |
| Titan | `titan` | `parts` |

- Skipet har plass til **6 enheter totalt**, uansett varetype.
- Du kan fly direkte mellom alle stasjoner. Reising er gratis, og varene tar ikke slutt.
- Du har **12 egne oppdrag**, hvert verdt **10 poeng**. Ingen andre kan ta oppdragene eller varene dine.
- Du må være på mottakerstasjonen med riktig last for å levere. Leveringen trekker varene fra skipet. Hvert oppdrag kan leveres én gang.
- Du kan losse på alle stasjoner. Varene kastes, og du får ingen poeng.
- I øvingen kan du nullstille posisjon, last og poeng. Kontoen beholdes.
- Konkurransen starter med ny spilltilstand. Da er nullstilling stengt. Instruktøren setter tiden; det er ingen grense på antall kommandoer.
- Når runden er satt på pause eller ferdig, kan du fortsatt lese status og oppdrag. Spillhandlinger er stengt.

<a id="funksjonsoversikt"></a>
## Funksjonsoversikt

Inne i kommandoen din lager du klienten med `game = GameClient.from_config()`. Deretter bruker du funksjonene under. Alle returnerer vanlige Python-dicts når de lykkes. Hvis noe feiler, får du en `GameError` i stedet; se [feilhåndtering](#feilmeldinger-og-hjelp).

| Hva du vil gjøre | Kall i Python | Returverdi |
|---|---|---|
| Se skipet | `game.status()` | [Spillerstatus](#spillerstatus) |
| Se stasjoner og varer | `game.map()` | [Kart med ei liste over stasjoner](#kart) |
| Liste oppdrag | `game.list_contracts(status="open")` | [Dict med lista `contracts`](#oppdragsliste) |
| Se ett oppdrag | `game.get_contract("P01")` | [Ett oppdrag direkte som dict](#ett-oppdrag) |
| Reise | `game.travel("luna")` | [Oppdatert spillerstatus](#reise) |
| Laste varer | `game.load_cargo("food", quantity=2)` | [Oppdatert spillerstatus](#lasting) |
| Kaste last | `game.unload_cargo("food", quantity=1)` | [Oppdatert spillerstatus](#lossing) |
| Levere | `game.deliver("P01")` | [Oppdatert spillerstatus](#levering) |
| Nullstille øving | `game.reset_practice()` | [Nullstilt spillerstatus](#nullstilling) |
| Se modus og tid | `game.session()` | [Dict med `mode` og `seconds_remaining`](#runden) |
| Bytte navn | `game.rename("Ada")` | [Dict med `name`](#navn) |

Eksemplene under viser returverdier fra spillet. Navn, ID-er, last, poeng og tid vil avhenge av spilleren og runden din.

<a id="spillerstatus"></a>
### Spillerstatus — `game.status()`

Tar ingen argumenter. Eksempel for en ny spiller i øvingen:

```python
{
    "player_id": "a1b2c3d4e5f6",
    "name": "Ada",
    "mode": "practice",
    "location": "earth",
    "cargo": {},
    "completed": [],
    "score": 0,
    "capacity": 6,
    "supplies_here": ["food", "water"],
}
```

| Felt | Python-type | Betydning |
|---|---|---|
| `player_id` | `str` | Spillerens ID. Dette er ikke innloggingstokenet. |
| `name` | `str` | Navnet i spillet. |
| `mode` | `str` | Rundens modus, f.eks. `practice` eller `running`. [Alle moduser](#runden). |
| `location` | `str` | ID-en til stasjonen skipet er på. |
| `cargo` | `dict[str, int]` | Vare → antall, f.eks. `{"food": 2, "water": 1}`. Tomt skip gir `{}`. |
| `completed` | `list[str]` | ID-ene til ferdige oppdrag, f.eks. `["P01"]`. |
| `score` | `int` | Poengsummen din i denne runden. |
| `capacity` | `int` | Maksimal last totalt. |
| `supplies_here` | `list[str]` | Varene du kan hente på denne stasjonen. |

Slik bruker du svaret:

```python
state = game.status()
print(f"Du er på {state['location']} og har {state['score']} poeng.")
print(f"Brukt plass: {sum(state['cargo'].values())}/{state['capacity']}")
for item, quantity in state["cargo"].items():
    print(f"{item}: {quantity}")
```

**Reise, lasting, lossing, levering og nullstilling returnerer hele denne strukturen**, med verdiene etter handlingen. Du trenger ikke hente status på nytt for å vise resultatet.

<a id="kart"></a>
### Kart — `game.map()`

Tar ingen argumenter. Returnerer:

```python
{
    "stations": [
        {"id": "earth", "name": "Earth", "supplies": ["food", "water"]},
        {"id": "luna", "name": "Luna", "supplies": ["tools"]},
        {"id": "mars", "name": "Mars", "supplies": ["medicine"]},
        {"id": "europa", "name": "Europa", "supplies": ["fuel"]},
        {"id": "titan", "name": "Titan", "supplies": ["parts"]},
    ],
    "travel_rule": "Any station is reachable directly. Travel is free.",
}
```

`stations` er lista over stasjoner. Bruk `id` når du reiser, `name` for visning og `supplies` for å vise hvilke varer som finnes der. `travel_rule` er en tekst som beskriver reiseregelen.

```python
data = game.map()
for station in data["stations"]:
    print(f"{station['name']} ({station['id']}): {', '.join(station['supplies'])}")
```

<a id="oppdragsliste"></a>
### Oppdragsliste — `game.list_contracts(status="all")`

| Argument | Type | Verdier | Standard hvis du utelater det |
|---|---|---|---|
| `status` | `str` | `"open"` = ledige, `"completed"` = ferdige, `"all"` = alle | `"all"` |

Returnerer en dict med nøkkelen `contracts`. Her er et **forkortet eksempel med ett oppdrag**; i starten inneholder lista alle 12:

```python
{
    "contracts": [
        {
            "id": "P01",
            "item": "food",
            "source": "earth",
            "destination": "luna",
            "quantity": 2,
            "reward": 10,
            "completed": False,
        },
    ],
}
```

Ingen treff gir `{"contracts": []}`. Det er ikke en feil. Feltene i hvert oppdrag er forklart under.

```python
data = game.list_contracts(status="open")
print(f"Du har {len(data['contracts'])} ledige oppdrag.")
```

<a id="ett-oppdrag"></a>
### Ett oppdrag — `game.get_contract(contract_id)`

`contract_id` er en påkrevd `str`, f.eks. `"P01"`. Hent ID-en fra oppdragslista. Returnerer oppdraget **direkte**, uten en `contracts`-liste rundt:

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

| Felt | Type | Betydning |
|---|---|---|
| `id` | `str` | ID-en du bruker for å hente eller levere oppdraget. |
| `item` | `str` | Varen du skal frakte. |
| `source` | `str` | ID-en til hentestedet. |
| `destination` | `str` | ID-en til mottakerstasjonen. |
| `quantity` | `int` | Hvor mange enheter du må levere. |
| `reward` | `int` | Hvor mange poeng leveringen gir. |
| `completed` | `bool` | `True` hvis du allerede har levert dette oppdraget. |

```python
contract = game.get_contract("P01")
print(f"Hent {contract['quantity']} {contract['item']} på {contract['source']}.")
print(f"Lever på {contract['destination']} for {contract['reward']} poeng.")
```

En ukjent ID gir `GameError` med `code="unknown_contract"`. Øvingsoppdrag starter med `P`, konkurranseoppdrag med `T`.

<a id="reise"></a>
### Reise — `game.travel(destination)`

`destination` er en påkrevd `str`: `"earth"`, `"luna"`, `"mars"`, `"europa"` eller `"titan"`. Bruk små bokstaver.

Flytter skipet direkte til stasjonen. Last og poeng beholdes. Returnerer [hele spillerstatusen](#spillerstatus); `location` og `supplies_here` beskriver den nye stasjonen.

```python
state = game.travel("luna")
print(state["location"])       # luna
print(state["supplies_here"])  # ['tools']
```

<a id="lasting"></a>
### Lasting — `game.load_cargo(item, quantity=1)`

| Argument | Type | Verdier | Standard |
|---|---|---|---|
| `item` | `str` | `"food"`, `"water"`, `"tools"`, `"medicine"`, `"fuel"`, `"parts"` | Må oppgis |
| `quantity` | `int` | Heltall fra 1 til 6 | `1` |

Du må være på en stasjon som har varen, og ha nok ledig plass. Antallet **legges til** lasten du allerede har. Returnerer [hele spillerstatusen](#spillerstatus).

Eksempel når skipet er tomt og står på Earth:

```python
state = game.load_cargo("food", quantity=2)
print(state["cargo"])  # {'food': 2}
```

Fullt skip gir `cargo_full`. En vare som ikke finnes på stasjonen gir `unavailable_cargo`.

<a id="lossing"></a>
### Lossing — `game.unload_cargo(item, quantity=1)`

Samme argumenter og standardverdi som lasting. Du må ha minst så mange enheter av varen i skipet. Du kan losse på alle stasjoner; det kaster varene og gir ingen poeng. Returnerer [hele spillerstatusen](#spillerstatus).

Eksempel når du har 2 `food` i skipet:

```python
state = game.unload_cargo("food", quantity=1)
print(state["cargo"])  # {'food': 1}
```

Hvis du losser den siste enheten, fjernes varen fra `cargo`. Ikke nok last gir `missing_cargo`.

<a id="levering"></a>
### Levering — `game.deliver(contract_id)`

`contract_id` er en påkrevd `str` fra oppdragslista. Du må være på mottakerstasjonen, ha minst riktig mengde av varen og ikke ha levert oppdraget før.

Funksjonen trekker den nødvendige lasten fra skipet, legger ID-en i `completed` og øker `score`. Returnerer [hele spillerstatusen](#spillerstatus), ikke oppdraget.

Eksempel på Luna, med nøyaktig 2 `food`, 0 poeng og ingen ferdige oppdrag i øvingen:

```python
state = game.deliver("P01")
print(state["score"])      # 10
print(state["cargo"])      # {}
print(state["completed"])  # ['P01']
```

Typiske feil: `wrong_station`, `missing_cargo`, `already_delivered` eller `unknown_contract`.

<a id="nullstilling"></a>
### Nullstilling — `game.reset_practice()`

Tar ingen argumenter og virker bare i øvingen. Setter skipet på Earth med tom last, ingen ferdige oppdrag og 0 poeng. Navn og spillerkonto beholdes. Returnerer [hele spillerstatusen](#spillerstatus).

**Funksjonen spør ikke om bekreftelse. Det gjør du i CLI-et før du kaller den**, for eksempel med `typer.confirm`.

```python
if typer.confirm("Nullstille posisjon, last og poeng i øvingen?"):
    state = game.reset_practice()
    print(f"Tilbake på {state['location']} med {state['score']} poeng.")
```

Utenfor øvingen får du `practice_only`.

<a id="runden"></a>
### Runden — `game.session()`

Tar ingen argumenter. Eksempel under en pågående konkurranse:

```python
{"mode": "running", "seconds_remaining": 1742}
```

| `mode` | Betydning | Kan du gjøre spillhandlinger? |
|---|---|---|
| `practice` | Øving | Ja, også nullstilling. |
| `lobby` | Venter på start | Nei. |
| `running` | Konkurransen pågår | Ja, men ikke nullstilling. |
| `paused` | Konkurransen er satt på pause | Nei. Klokka er også satt på pause. |
| `finished` | Runden er ferdig | Nei. |

`seconds_remaining` er et heltall. I lobbyen er det planlagt rundetid; under konkurransen er det tiden som gjenstår. I øvingen er verdien ikke en nedtelling og kan ignoreres.

```python
data = game.session()
print(f"Modus: {data['mode']}")
if data["mode"] != "practice":
    minutes, seconds = divmod(data["seconds_remaining"], 60)
    print(f"Tid igjen: {minutes}:{seconds:02d}")
```

<a id="navn"></a>
### Navn — `game.rename(name)`

`name` er en påkrevd `str` på 1–32 tegn. Navnet må være ledig og kan inneholde bokstaver, tall, understrek, mellomrom, punktum og bindestrek. Et navn med bare mellomrom er ikke gyldig. Du kan bare endre navn i øvingen.

```python
data = game.rename("Ada")
# data er: {"name": "Ada"}
print(f"Navnet ditt er nå {data['name']}.")
```

Returnerer bare `name`, ikke spillerstatus. Et opptatt navn gir `name_taken`; utenfor øvingen får du `practice_only`.

<a id="feilmeldinger-og-hjelp"></a>
## Feilmeldinger og hjelp

Bruk `try`/`except` som i `status` og eksemplet med `oppdrag`. **Både `GameClient.from_config()` og selve spillkallet skal være inne i `try`.** Da får du også håndtert manglende spilleroppsett.

Når et kall mislykkes, får du en `GameError` i stedet for returverdien beskrevet over:

| Felt på feilen | Type | Hva du bruker det til |
|---|---|---|
| `exc.message` | `str` | Forklare hva som gikk galt. Serverens meldinger er på engelsk. |
| `exc.hint` | `str` | Vise hva brukeren kan gjøre videre. Kan være tom. |
| `exc.code` | `str` | Kjenne igjen en bestemt feil, f.eks. `cargo_full`. |

Print feil til `sys.stderr` og avslutt med `raise typer.Exit(1)`. Da kan vanlig output, særlig JSON, fortsatt brukes av andre programmer. Legg API-kallene inne i kommandoene, så `--help` fungerer uten serverkontakt.

| Feilkode / problem | Hva brukeren kan gjøre |
|---|---|
| `cargo_full` | Lever eller loss noe. Grensen er 6 enheter totalt. |
| `unavailable_cargo` | Sjekk hentestedet i oppdraget eller kartet, og reis dit. |
| `wrong_station` | Reis til oppdragets `destination`. |
| `missing_cargo` | Sjekk `cargo` og oppdragets `quantity`. |
| `already_delivered` | Velg et annet ledig oppdrag. |
| `unknown_contract` | Hent oppdragslista på nytt; ID-ene endres mellom øving og konkurranse. |
| `round_inactive` | Vent på start eller på at instruktøren fortsetter runden. |
| `practice_only` | Handlingen er bare tillatt i øvingen. |
| `invalid_input` | Sjekk verdiene du sender inn. Antall skal f.eks. være et heltall fra 1 til 6. |
| `configuration` | Kjør `uv run python -m verktoy.oppsett`. |
| `unauthorized` eller mistet token | Si fra, så hjelper instruktøren med spillerkontoen. |
| `connection` eller `timeout` | Sjekk status før du gjentar handlingen. Endringen kan ha gått gjennom selv om svaret forsvant. |

Feil under registrering? Si fra, så sjekker vi om du ble registrert. Ikke lag flere kontoer for å prøve igjen. Hvis nettforbindelsen feiler med en gang, vis instruktøren feilmeldingen.

Vanligvis leses serveradresse og token fra `.player.json`. Hvis du har satt `ORBITAL_URL` eller `ORBITAL_TOKEN`, bruker klienten disse verdiene i stedet.
