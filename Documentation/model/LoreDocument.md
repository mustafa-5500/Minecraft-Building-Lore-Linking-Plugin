# LoreDocument

> **Software Detailed Documentation:** [LoreDocument_SDD.md](./LoreDocument_SDD.md)  
> **Source File:** [LoreDocument.java](../../src/main/java/org/almond/buildinglore/model/LoreDocument.java)

A named lore document attached to a Selection.
Contains ordered text entries that players can read.

---

## Table of Contents

**Fields:**
- `id` (`UUID`) — TODO: describe field
- `name` (`String`) — TODO: describe field
- `entries` (`List<String>`) — TODO: describe field
- `createdAt` (`long`) — TODO: describe field

**Functions:**
- [LoreDocument (Constructor)](#loredocument)
- [addEntry](#addentry)
- [removeEntry](#removeentry)
- [getFullText](#getfulltext)
- [getId](#getid)
- [getName](#getname)
- [getEntries](#getentries)
- [getCreatedAt](#getcreatedat)
- [getEntryCount](#getentrycount)

---

## LoreDocument (Constructor)

### Signature
```java
public LoreDocument(UUID id, String name, List<String> entries, long createdAt)
```

### Description
TODO: Describe what `LoreDocument` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `id` | `UUID` | TODO: describe |
| `name` | `String` | TODO: describe |
| `entries` | `List<String>` | TODO: describe |
| `createdAt` | `long` | TODO: describe |

### Returns
`LoreDocument` instance.

---

## LoreDocument (Constructor)

### Signature
```java
public LoreDocument(String name)
```

### Description
TODO: Describe what `LoreDocument` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `name` | `String` | TODO: describe |

### Returns
`LoreDocument` instance.

---

## addEntry

### Signature
```java
public void addEntry(String text)
```

### Description
TODO: Describe what `addEntry` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `text` | `String` | TODO: describe |

### Returns
`void`

---

## removeEntry

### Signature
```java
public boolean removeEntry(int index)
```

### Description
TODO: Describe what `removeEntry` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `index` | `int` | TODO: describe |

### Returns
`boolean` — TODO: describe return value.

---

## getFullText

### Signature
```java
public String getFullText()
```

### Description
TODO: Describe what `getFullText` does.

### Parameters
None.

### Returns
`String` — TODO: describe return value.

---

## getId

### Signature
```java
public UUID getId()
```

### Description
TODO: Describe what `getId` does.

### Parameters
None.

### Returns
`UUID` — TODO: describe return value.

---

## getName

### Signature
```java
public String getName()
```

### Description
TODO: Describe what `getName` does.

### Parameters
None.

### Returns
`String` — TODO: describe return value.

---

## getEntries

### Signature
```java
public List<String> getEntries()
```

### Description
TODO: Describe what `getEntries` does.

### Parameters
None.

### Returns
`List<String>` — TODO: describe return value.

---

## getCreatedAt

### Signature
```java
public long getCreatedAt()
```

### Description
TODO: Describe what `getCreatedAt` does.

### Parameters
None.

### Returns
`long` — TODO: describe return value.

---

## getEntryCount

### Signature
```java
public int getEntryCount()
```

### Description
TODO: Describe what `getEntryCount` does.

### Parameters
None.

### Returns
`int` — TODO: describe return value.

---

## See Also

- **Software Detailed Design:** [LoreDocument_SDD.md](./LoreDocument_SDD.md)
