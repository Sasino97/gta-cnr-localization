# CnR V Localization

This repository contains the necessary files for the localization of CnR. 

## Workflow

The repository is reviewed through pull requests. The validation workflow runs on every push and on pull requests targeting `master`.

Typical editing flow:

1. Open the repository in Visual Studio Code.
2. Sync or pull the latest changes before editing.
3. Translate or adjust the relevant XML file.
4. Run the validator locally.
5. Commit your changes and open or update a pull request.

If you get a merge conflict, keep both valid changes where possible and prefer the correct translation over a broken XML structure.

## Setup

Install the required tools:

- [Visual Studio Code](https://code.visualstudio.com/download)
- [Git](https://git-scm.com/download/)
- Python 3.11 or newer

Clone the repository:

```bash
git clone https://github.com/Sasino97/gta-cnr-localization.git
```

Optional packages:

```bash
pip install colorama dominate
```

`colorama` enables colored terminal output. `dominate` is only needed for the HTML formatting preview.

## Validation

Run the validator after editing translations:

```bash
python validator.py
```

Show missing translations for one language:

```bash
python validator.py --show_lang de-DE
```

Treat warnings as errors:

```bash
python validator.py --treat_warnings_as_errors
```

Generate the HTML formatting preview:

```bash
python validator.py --preview_formatting
```

The validator checks for:

- Missing or duplicate strings
- Unsupported language codes
- Missing or invalid GTA formatting tags
- Variable mismatches
- Empty translations
- Punctuation placement issues
- Excess spacing

Punctuation checks are skipped for `zh-Hans`, `zh-Hant`, and `ar-001` because their sentence structure is different.

## XML Format

Every translation file uses this structure:
- String: Each `String` uses `xml:lang` to identify the locale
- Entry: an abstract message used by game code, containing multiple Strings — one per language.
- Entries: the root container holding all Entry elements in an XML file.

Example:

```xml
<Entry Id="some_id">
    <String xml:lang="en-US">Example text</String>
    <String xml:lang="de-DE">Beispieltext</String>
</Entry>
```

## Translation Rules

Remember that this is a game, keep the translation chilled, and not too formal.

If the `en-US` translation does not make sense in the respective language, change the texts so that the user understands them.

### Variables

Variables use numbered placeholders such as `{0}`, `{1}`, and `{2}`. The numbers must stay intact, but their order can change if the target language needs a different sentence structure.

Example:

```xml
<String xml:lang="en-US">{0} killed {1} {2}.</String>
<String xml:lang="zh-Hans">{0} {2} 杀了 {1}.</String>
```

In this example, 0 is the killer, 1 is the victim and 2 is the weapon/method of killing. I have used Chinese in this example, because in English we say

> X has killed Y with a knife

but in Chinese they say

> X 用刀杀了 Y (X with a knife has killed Y)

So this was a good example to show you how variable `{2}` is moved before `{1}` in this scenario.

### Escaping the bracket character

This is unlikely to actually happen, but if you need to actually show the `{` or `}` characters, you simply type them twice:

```xml
<String xml:lang="en-US">This is a left bracket: {{</String>
```

### Special XML characters

If you want to display the following characters literally, they <b>MUST</b> be escaped as follows:

```xml
<    &lt;
>    &gt;
&    &amp;
```

For example, you <b>cannot</b> write:

```xml
<String xml:lang="en-US">You have > 10 items</String> <!-- BAD EXAMPLE -->
```

You must replace the quotes with their appropriate escape code:

```xml
<String xml:lang="en-US">You have &gt; 10 items</String>
```

Otherwise you will break the whole XML file and it won't load. The same applies to all those characters shown above.

### Unnecessary escapes

The following characters should be escaped in a standard XML file, however, the parser we are using doesn't have issues with those, so we'll not escape them and we'll use the literal strings, for simplicity.

```
"    &quot;
'    &apos;
```

So, it's OK to write

```xml
<String xml:lang="en-US">You can't do that</String>
```

### Consistency

When you translate certain technical terms of the game, choose the best that you can choose, a term that applies in all cases, and then stick to it. For example, if you choose to translate `Inventory` in a certain way, then stick to that term in all the translation, don't suddenly change it to `Backpack` or `Pocket` in other parts of the UI.

### Comments

Have you ever found one of those websites where something is grammatically correct but it makes no sense in that context? Well, whether you have encountered such a website or not, we definitely don't want to commit that mistake, that's why there are comments in the code, and you can add your own if you think they are necessary.

This is a simple comment in XML

```xml
<!-- This string is shown when the player opens the main menu -->
```

It explains to translators and all readers what the intentions of the original author of that portion of code were.

Then we have section comments:

```xml
    <!-- ========================= -->
    <!-- Kill Messages -->
    <!-- ========================= -->
```

These delimit different categories of message inside the same file, and help keep it organized.

### GTA Formatting

Line breaks use `\n` or `~n~`.

Color tags such as `~r~` and `~s~` must be preserved when they appear in the source string. The validator also checks that formatting tags are used consistently between languages.
[List of GTA Colors](https://wiki.rage.mp/index.php?title=Fonts_and_Colors#GTA_Colors).

### Highlighting

Text can also be highlighted with the `(C)(/C)` tags.

```xml
(C)WORD TO HIGHLIGHT(/C)
```

[Highlighting](https://wiki.rage.mp/index.php?title=Fonts_and_Colors#Highlighting)

## Used ISO Language Codes

- English (US): `en-US`
- German (Germany): `de-DE`
- French (France): `fr-FR`
- Dutch (Netherlands): `nl-NL`
- Czech (Czechia) `cs-CZ`
- Danish (Denmark) `da-DK`
- Italian (Italy): `it-IT`
- Spanish (Spain): `es-ES`
- Portuguese (Brazil): `pt-BR`
- Polish (Poland): `pl-PL`
- Turkish (Turkey): `tr-TR`
- Hindi (Latin Alphabet): `hi-Latn`
- Arabic (Modern Standard): `ar-001`
- Chinese (Simplified): `zh-Hans`
- Chinese (Traditional): `zh-Hant`
- Vietnamese (Vietnam): `vi-VN`
- Thai (Thailand): `th-TH`
- Indonesian (Indonesia): `id-ID`

## Help

You can use the guide in the thread "Using GitHub Desktop for translations" for step-by-step guidance. 
If you are unsure about a translation or validator error, ask a translator on our [Discord](https://discord.gg/cnr).
