# Nowe repozytorium GitHub (demo + backup)

Tworzysz dwa repozytoria na GitHubie dla projektu kvcskr w ustalonym formacie.

## Jak działasz

Użytkownik poda:
- `$ARGUMENTS` — nazwa projektu i krótki opis, np. `specfood-restauracje Skrypt wykrywający nowe restauracje w Polsce`

Pierwsza część to nazwa (do myślnika lub spacji), reszta to opis.

## Kroki

1. Zapytaj użytkownika o:
   - Nazwę projektu (jeśli nie podana w $ARGUMENTS)
   - Krótki opis (1 zdanie)
   - Stack technologiczny (Python? React? n8n? Make.com?)
   - Problem który rozwiązuje (1-2 zdania)
   - Jak działa (2-3 zdania)

2. Wygeneruj README według szablonu poniżej

3. Utwórz repo `nazwa-demo` (publiczne) przez gh CLI:
   ```
   gh repo create kvcskr/nazwa-demo --public --description "opis"
   ```

4. Utwórz repo `nazwa-backup` (prywatne):
   ```
   gh repo create kvcskr/nazwa-backup --private --description "opis (backup z kluczami)"
   ```

5. Zainicjuj lokalne repo, dodaj README, zrób pierwszy commit i push do demo

## Szablon README (zawsze w tym formacie)

```markdown
# [Narzędzie/Platforma] — [Opis projektu]

[Jedno zdanie wprowadzające co to jest i dla kogo]

## The Problem It Solves

[2-3 zdania opisujące problem biznesowy/techniczny który rozwiązuje projekt]

## How It Works

[Opis działania krok po kroku. Jeśli jest kilka scenariuszy/modułów — podziel na ### Part 1, ### Part 2 itd.]

## Tech Stack

| Komponent | Technologia |
|-----------|-------------|
| [komponent] | [technologia] |

## File Structure

```
[struktura plików projektu]
```

## Setup

1. [krok 1]
2. [krok 2]
3. [krok 3]

## Notes

[Uwagi dotyczące bezpieczeństwa, GDPR, ograniczeń, kredencjałów — repo demo nie zawiera kluczy API ani danych wrażliwych]
```

## Ważne zasady bezpieczeństwa

- Repo **demo** (publiczne): NIGDY nie zawiera kluczy API, tokenów, haseł, plików .env
- Repo **backup** (prywatne): pełny kod z kluczami, tylko dla właściciela
- Zawsze dodaj .gitignore do demo z wykluczeniem: .env, *.json z credentials, secrets/

## Format nazw repozytoriów

- demo: `nazwa-projektu-demo` (publiczne, dla rekruterów/portfolio)
- backup: `nazwa-projektu-backup` (prywatne, pełny kod)
