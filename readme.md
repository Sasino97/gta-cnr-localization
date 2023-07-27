# GTA CnR Localization
This repository contains the necessary files for the localization of CnR.

## Setup
### Download and Install the Required Software
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Git](https://git-scm.com/download/)

### Clone the Repository
- Open VSCode
- Select `File > Open Folder`
- Navigate to a folder of your liking
- Then select `Terminal > New Terminal`
- Run the following command: `git clone https://github.com/Sasino97/gta-cnr-localization.git`

### Troubleshooting
#### Missing permissions?
Login to GitHub by following the steps on screen, make sure to use the same account that has access to this page.

#### Must set username/email before committing?
- In a VSCode Terminal, run `git config --global user.name "USERNAME"`
- Then `git config --global user.email "NAME@EXAMPLE.COM"`

Obviously, replace those placeholders with your actual data.

## Format
The file format utilized for translations is XML (Extensible Markup Language). You can learn more about XML on [Wikipedia](https://en.wikipedia.org/wiki/XML). We will use a different XML file for each category, to have better separation.

## Index.json
Every new XML file that gets added to the project must be defined in this index file which uses the JSON format instead for simplicity. The file itself is simple and self-explanatory.

## Object types
I have defined the following XML objects:
- Entry: an abstract message containing multiple strings that convey that message. The game code will use these units, then the underlying system will pick the correct string depending on the user's language.
- String: a string of characters with the actual text content to display, and a language property indicating for what language it is meant.

## Basic Structure
Each file contains a root `Entries` array. Each element of this array is an `Entry` object with an `Id` property which <b>MUST</b> be unique. In case of a duplicate ID, the parser will only take the first encountered in consideration and will ignore any subsequent duplicate. You will normally not need to worry about this, as Sasino himself will add all the entries.

Each `Entry` object then contains multiple `String` child objects, that have a `xml:lang` standard property containing the locale code (e.g. en-US) of the translation, and the actual string as its content; duplicate translations in the same language of the same `String` will be ignored. 

## Variables
Strings can contain variables which are defined using the following bracket symbols: `{` to open and `}` to close. A variable cannot have a name, but only a number, but they can be in any order, just make sure to match them correctly if the language you are translating in doesn't follow the same sentence order.

### Example
```xml
<String xml:lang="en-US">{0} killed {1} {2}.</String>
<String xml:lang="zh-Hans">{0} {2} 杀了 {1}.</String>
```

In this example, 0 is the killer, 1 is the victim and 2 is the weapon/method of killing. I have used Chinese in this example, because in English we say
> X has killed Y with a knife

but in Chinese they say 
> X用刀杀了Y (X with a knife has killed Y)

So this was a good example to show you how variable `{2}` is moved before `{1}` in this scenario.

### Escaping the bracket character
This is unlikely to actually happen, but if you need to actually show the `{` or `}` characters, you simply type them twice:
```xml
<String xml:lang="en-US">This is a left bracket: {{</String>
```

## Special XML characters
If you want to display the following characters literally, they <b>MUST</b> be escaped as follows:
```xml
"    &quot;
'    &apos;
<    &lt;
>    &gt;
&    &amp;
```

For example, you <b>cannot</b> write:
```
<String xml:lang="en-US">Your crew name is "SWAT"</String> <!-- BAD EXAMPLE -->
```
You must replace the quotes with their appropriate escape code:
```xml
<String xml:lang="en-US">Your crew name is &quot;SWAT&quot;</String>
```

Otherwise you will break the whole XML file and it won't load. The same applies to all those characters shown above.

## Comments
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

## GTA Formatting

### Colors
Sometimes you will find strings that contain symbols like the following: `~r~`. This simply means that from there on, the string will become red. Another common one is `~s~`, which will erase color formatting and return to the default color (white or black depending on the background). That how GTA color coding works, and we make extensive use of those in CnR because we have used the native GUI of GTA V a lot, and that's the way colors are coded.

When you are translating from English to another language and there is color formatting, you need to try to best of your ability to colorize the corresponding words, and not to change the colors to other colors.

[List of GTA Colors](https://wiki.rage.mp/index.php?title=Fonts_and_Colors#GTA_Colors).

### Highlighting
Text can also be highlighted with the `<C></C>` tags. Unfortunately, since those tags are XML-like, but they are not to be interpreted by my script but by GTA, they have to be escaped, so if you ever find them in the strings to translate, they will actually be like this:
```xml
&lt;C&gt;WORD TO HIGHLIGHT&lt;/C&gt;
```

[Highlighting](https://wiki.rage.mp/index.php?title=Fonts_and_Colors#Highlighting)

## Used ISO Language Codes
- English (US): `en-US`
- Spanish (Spain): `es-ES`
- French (France): `fr-FR`
- German (Germany): `de-DE`
- Polish (Poland): `pl-PL`
- Chinese (Simplified): `zh-Hans`
- Chinese (Traditional): `zh-Hant`
- Arabic (Brazil): `pt-BR`
- Italian (Italy): `it-IT`
- Dutch (Netherlands): `nl-NL`
- Arabic (Modern Standard): `ar-001`
- Vietnamese (Vietnam): `vi-VN`
- Thai (Thailand): `th-TH`