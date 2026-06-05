# LoreDocumentManager

> **Software Detailed Documentation:** [LoreDocumentManager_SDD.md](./LoreDocumentManager_SDD.md)  
> **Source File:** [LoreDocumentManager.java](../../src/main/java/org/almond/buildinglore/manager/LoreDocumentManager.java)

Manages the chat-based input flow for creating and editing lore documents.
Tracks per-player state: whether they are naming a new document or adding text to one.

---

## Table of Contents

**Fields:**
- `mode` (`InputMode`) — TODO: describe field
- `selectionName` (`String`) — TODO: describe field
- `documentName` (`String`) — TODO: describe field

**Functions:**
- [getMode](#getmode)
- [getSelectionName](#getselectionname)
- [getDocumentName](#getdocumentname)
- [startNaming](#startnaming)
- [startWriting](#startwriting)
- [hasPendingInput](#haspendinginput)
- [getInputState](#getinputstate)
- [clearInput](#clearinput)

---

## getMode

### Signature
```java
public InputMode getMode()
```

### Description
TODO: Describe what `getMode` does.

### Parameters
None.

### Returns
`InputMode` — TODO: describe return value.

---

## getSelectionName

### Signature
```java
public String getSelectionName()
```

### Description
TODO: Describe what `getSelectionName` does.

### Parameters
None.

### Returns
`String` — TODO: describe return value.

---

## getDocumentName

### Signature
```java
public String getDocumentName()
```

### Description
TODO: Describe what `getDocumentName` does.

### Parameters
None.

### Returns
`String` — TODO: describe return value.

---

## startNaming

### Signature
```java
public void startNaming(UUID player, String selectionName)
```

### Description
TODO: Describe what `startNaming` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `UUID` | TODO: describe |
| `selectionName` | `String` | TODO: describe |

### Returns
`void`

---

## startWriting

### Signature
```java
public void startWriting(UUID player, String selectionName, String documentName)
```

### Description
TODO: Describe what `startWriting` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `UUID` | TODO: describe |
| `selectionName` | `String` | TODO: describe |
| `documentName` | `String` | TODO: describe |

### Returns
`void`

---

## hasPendingInput

### Signature
```java
public boolean hasPendingInput(UUID player)
```

### Description
TODO: Describe what `hasPendingInput` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `UUID` | TODO: describe |

### Returns
`boolean` — TODO: describe return value.

---

## getInputState

### Signature
```java
public InputState getInputState(UUID player)
```

### Description
TODO: Describe what `getInputState` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `UUID` | TODO: describe |

### Returns
`InputState` — TODO: describe return value.

---

## clearInput

### Signature
```java
public void clearInput(UUID player)
```

### Description
TODO: Describe what `clearInput` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `UUID` | TODO: describe |

### Returns
`void`

---

## See Also

- **Software Detailed Design:** [LoreDocumentManager_SDD.md](./LoreDocumentManager_SDD.md)
