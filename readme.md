# Locales
This folder contains the necessary files for the localization of CnR.

## Index.json
Every new XML file that gets added to the project must be defined in this index file which uses the JSON format instead for simplicity. The file itself is simple and self-explanatory.

## Format
The file format utilized for translations is XML (Extensible Markup Language). You can learn more about the simple structure of a XML file on [Wikipedia](https://en.wikipedia.org/wiki/XML).

## Basic Structure
Each file contains a root `Entries` array. Each element of this array is an `Entry` object with an `Id` property which <b>MUST</b> be unique. In case of a duplicate ID, the parser will only consider the first encountered and will ignore any subsequent duplicate. Each `Entry` object then contains multiple `String` child objects, that have a `xml:lang` standard property containing the locale code (e.g. en-US) of the translation, and the actual string as its content; duplicate translations in the same language of the same `String` will be ignored. 

## Variables
Strings can contain variables which are defined using the following bracket symbols: `{` to open and `}` to close. A variable cannot have a name, but only a number, but they can be in any order, just make sure to match them correctly if the language you are translating in doesn't follow the same sentence order.

### Example
```xml
<String xml:lang="en-US">{0} killed {1} {2}.</String>
<String xml:lang="zh-Hans">{0} {2} 杀了 {1}.</String>
```

In this example, 0 is the killer, 1 is the victim and 2 is the weapon/method of killing. I have used Chinese (Simplified) in this example, because in English we say
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
The following characters <b>MUST</b> be escaped as follows:
```xml
"    &quot;
'    &apos;
<    &lt;
>    &gt;
&    &amp;
```

For example, you <b>cannot</b> write:
```xml
<String xml:lang="en-US">Your crew name is "SWAT"</String>
```
You must replace the quotes with their appropriate escape code:
```xml
<String xml:lang="en-US">Your crew name is &quot;SWAT&quot;</String>
```

Otherwise you will break the whole XML file and it won't load.
