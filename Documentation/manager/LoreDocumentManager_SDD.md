# LoreDocumentManager — Software Detailed Design

> **API Documentation:** [LoreDocumentManager.md](./LoreDocumentManager.md)  
> **Source File:** [LoreDocumentManager.java](../../src/main/java/org/almond/buildinglore/manager/LoreDocumentManager.java)

---

## 1. Overview

Manages the chat-based input flow for creating and editing lore documents.
Tracks per-player state: whether they are naming a new document or adding text to one.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.manager;
```

```java
import org.almond.buildinglore.model.LoreDocument;
import org.almond.buildinglore.model.Selection;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
```

| Import | Purpose |
|--------|---------|
| [`LoreDocument`](../model/LoreDocument.md) | TODO: describe purpose |
| [`Selection`](../model/Selection.md) | TODO: describe purpose |
| `HashMap` | TODO: describe purpose |
| `Map` | TODO: describe purpose |
| `UUID` | TODO: describe purpose |

---

## 3. Class Declaration

```java
public class LoreDocumentManager {
```


---

## 4. Instance Fields

```java
private final InputMode mode;
private final String selectionName;
private final String documentName;
```

| Field | Type | Description |
|-------|------|-------------|
| `mode` | `InputMode` | TODO: describe |
| `selectionName` | `String` | TODO: describe |
| `documentName` | `String` | TODO: describe |

---

## 5. `getMode()`

```java
public InputMode getMode()
```

TODO: Provide detailed design explanation for `getMode`.

---

## 6. `getSelectionName()`

```java
public String getSelectionName()
```

TODO: Provide detailed design explanation for `getSelectionName`.

---

## 7. `getDocumentName()`

```java
public String getDocumentName()
```

TODO: Provide detailed design explanation for `getDocumentName`.

---

## 8. `startNaming()`

```java
public void startNaming(UUID player, String selectionName)
```

TODO: Provide detailed design explanation for `startNaming`.

---

## 9. `startWriting()`

```java
public void startWriting(UUID player, String selectionName, String documentName)
```

TODO: Provide detailed design explanation for `startWriting`.

---

## 10. `hasPendingInput()`

```java
public boolean hasPendingInput(UUID player)
```

TODO: Provide detailed design explanation for `hasPendingInput`.

---

## 11. `getInputState()`

```java
public InputState getInputState(UUID player)
```

TODO: Provide detailed design explanation for `getInputState`.

---

## 12. `clearInput()`

```java
public void clearInput(UUID player)
```

TODO: Provide detailed design explanation for `clearInput`.

---
