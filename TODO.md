For the 1.8.x series, a couple a features are being migrated from the
application to the server. In the move, we rewrite it to manipulate the DOM
with appropriate tools rather than preg, and bring unit tests to ensure
overall QA.

Nonetheless, some features could not be migrated in time. This is the list of
the features that have been removed from the application and not yet added back
to the server:

- Correctly style <p> inside <blockquote>
- Correctly style references
- [PARTIAL] Fix R/, V/ formating
- Fix inflexion markers
- Fix acclamation, antienne, verse, repons

*R/ V/ formating*
```java
// R/, V/ formating
.replace("</p></font></p>", "</font></p>")
.replaceAll("[.,!?:;]\\s*([R|V]/\\s*[A-Za-z0-9])", "<br/> $1") // Split lines...
.replaceAll("(?!\\s)([R|V])/", " $1/") // Ensure space before
.replaceAll("([R|V])/(?!\\s)", "$1/ ") // Ensure space after
.replaceAll("([R|V])/\\s*<p>", "$1/ ")
.replace(", R/", "<br/>R/") // special case for lectures office introduction. *sights*
.replaceAll("([R|V])/ (?!(</font>)?\\s*(</p>|<br\\s*/?>))", " <strong>$1/&nbsp;</strong>")
```

*Reference formating*
```
// clean references
.replaceAll("<small><i>\\s*\\((cf.)?\\s*", "<small><i>— ")
.replaceAll("\\s*\\)</i></small>", "</i></small>")
```

*Infexion markers*
```java
// inflexion fixes && accessibility
.replaceAll("([+*])\\s*<br", "<sup>$1</sup><br")
.replaceAll("<sup", "<sup aria-hidden=true")
// ensure punctuation/inflexions have required spaces
.replaceAll("\\s*(<sup)", "&nbsp;$1")
.replaceAll("\\b(?<!&)(?<!&#)(\\w+);\\s*", "$1&#x202f;; ")
```

*Acclamation, verse, repons*
```java
// Evangile fixes
.replace("<br /><blockquote>", "<blockquote>")
.replaceAll("<b>Acclamation\\s*:\\s*</b>", "")
```

