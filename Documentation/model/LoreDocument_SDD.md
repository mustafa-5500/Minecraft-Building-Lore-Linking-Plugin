# LoreDocument — Software Detailed Design

> **API Documentation:** [LoreDocument.md](./LoreDocument.md)  
> **Source File:** [LoreDocument.java](../../src/main/java/org/almond/buildinglore/model/LoreDocument.java)

---

## 1. Overview

A named lore document attached to a Selection.
Contains ordered text entries that players can read.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.model;
```

```java
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
```

| Import | Purpose |
|--------|---------|
| `ArrayList` | TODO: describe purpose |
| `List` | TODO: describe purpose |
| `UUID` | TODO: describe purpose |

---

## 3. Class Declaration

```java
public class LoreDocument {
```


---

## 4. Instance Fields

```java
private final UUID id;
private final String name;
private final List<String> entries;
private final long createdAt;
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | TODO: describe |
| `name` | `String` | TODO: describe |
| `entries` | `List<String>` | TODO: describe |
| `createdAt` | `long` | TODO: describe |

---

## 5. Constructor

```java
public LoreDocument(UUID id, String name, List<String> entries, long createdAt)
```

TODO: Provide detailed design explanation for `LoreDocument`.

---

## 6. Constructor

```java
public LoreDocument(String name)
```

TODO: Provide detailed design explanation for `LoreDocument`.

---

## 7. `addEntry()`

```java
public void addEntry(String text)
```

TODO: Provide detailed design explanation for `addEntry`.

---

## 8. `removeEntry()`

```java
public boolean removeEntry(int index)
```

TODO: Provide detailed design explanation for `removeEntry`.

---

## 9. `getFullText()`

```java
public String getFullText()
```

TODO: Provide detailed design explanation for `getFullText`.

---

## 10. `getId()`

```java
public UUID getId()
```

TODO: Provide detailed design explanation for `getId`.

---

## 11. `getName()`

```java
public String getName()
```

TODO: Provide detailed design explanation for `getName`.

---

## 12. `getEntries()`

```java
public List<String> getEntries()
```

TODO: Provide detailed design explanation for `getEntries`.

---

## 13. `getCreatedAt()`

```java
public long getCreatedAt()
```

TODO: Provide detailed design explanation for `getCreatedAt`.

---

## 14. `getEntryCount()`

```java
public int getEntryCount()
```

TODO: Provide detailed design explanation for `getEntryCount`.

---
