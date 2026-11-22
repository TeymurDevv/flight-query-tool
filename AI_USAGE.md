# AI Use Disclosure

## Tool used

- OpenAI Codex, GPT-6.
- AI conversation: [Flight Query Tool Q&A](https://chatgpt.com/s/cx_6b037320f6c48191a7acf414fa461193)

## How AI helped

I used Codex to understand Python concepts and get the explanations and code
examples below. Codex also helped draft implementation code in the required
modules. The starter structure and sample files came from the Moodle materials;
this disclosure does not claim that the entire project package was generated
by AI.

## Questions asked and answers received

### 1. Why strip CSV fields before validating them?

CSV input can have extra spaces around a value, such as `" RIX "`. Calling
`strip()` removes those spaces so validation checks the actual airport code.

```python
values = [field.strip() for field in fields]
```

### 2. Why use both `fullmatch()` and `strptime()` for a date?

`fullmatch()` checks that the whole string follows the required
`YYYY-MM-DD HH:MM` shape. `strptime()` then checks that the date and time
actually exist, so a value such as `2026-02-31 09:30` is rejected.

```python
if not DATE_PATTERN.fullmatch(value):
    raise ValueError("Date and time must use YYYY-MM-DD HH:MM.")
return datetime.strptime(value, "%Y-%m-%d %H:%M")
```

### 3. Why use both `flight_id` and `departure_datetime` as the duplicate key?

The pair identifies one scheduled flight. The same flight ID may be used for
departures at different times, so the departure time distinguishes them.

```python
key = (flight_id, departure_datetime)
if key in seen:
    print("Duplicate flight")
else:
    seen.add(key)
```

### 4. How does the `seen` set check/add operation work?

The set remembers each pair that has appeared. If the pair is already in the
set, it is a duplicate; otherwise, adding it marks it as seen for later rows.

```python
if key in seen:
    print("Duplicate flight")
else:
    seen.add(key)
```

### 5. What does an `argparse` mutually exclusive group do?

It makes `-i`, `-d`, and `-j` alternatives. Since the group is required, the
user must provide exactly one input source.

```python
source = parser.add_mutually_exclusive_group(required=True)
source.add_argument("-i", metavar="FILE")
source.add_argument("-d", metavar="FOLDER")
source.add_argument("-j", metavar="FILE")
```

