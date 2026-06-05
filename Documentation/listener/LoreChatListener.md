# LoreChatListener

> **Software Detailed Documentation:** [LoreChatListener_SDD.md](./LoreChatListener_SDD.md)  
> **Source File:** [LoreChatListener.java](../../src/main/java/org/almond/buildinglore/listener/LoreChatListener.java)

Listens for chat messages from players who are in lore input mode.
Captures their message as either a document name or lore text entry.

---

## Table of Contents

**Fields:**
- `PREFIX` (`String`) — TODO: describe field
- `loreManager` ([`LoreDocumentManager`](../manager/LoreDocumentManager.md)) — TODO: describe field
- `storageManager` ([`SelectionStorageManager`](../manager/SelectionStorageManager.md)) — TODO: describe field

**Functions:**
- [LoreChatListener (Constructor)](#lorechatlistener)
- [onChat](#onchat)
- [handleNaming](#handlenaming)
- [handleWriting](#handlewriting)

---

## LoreChatListener (Constructor)

### Signature
```java
public LoreChatListener(LoreDocumentManager loreManager, SelectionStorageManager storageManager)
```

### Description
TODO: Describe what `LoreChatListener` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `loreManager` | [`LoreDocumentManager`](../manager/LoreDocumentManager.md) | TODO: describe |
| `storageManager` | [`SelectionStorageManager`](../manager/SelectionStorageManager.md) | TODO: describe |

### Returns
`LoreChatListener` instance.

---

## onChat

### Signature
```java
@EventHandler(priority = EventPriority.LOWEST)
public void onChat(AsyncPlayerChatEvent event)
```

### Description
TODO: Describe what `onChat` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `event` | `AsyncPlayerChatEvent` | TODO: describe |

### Returns
`void`

---

## handleNaming

### Signature
```java
private void handleNaming(Player player, InputState state, String name)
```

### Description
TODO: Describe what `handleNaming` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `Player` | TODO: describe |
| `state` | `InputState` | TODO: describe |
| `name` | `String` | TODO: describe |

### Returns
`void`

---

## handleWriting

### Signature
```java
private void handleWriting(Player player, InputState state, String text)
```

### Description
TODO: Describe what `handleWriting` does.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `player` | `Player` | TODO: describe |
| `state` | `InputState` | TODO: describe |
| `text` | `String` | TODO: describe |

### Returns
`void`

---

## See Also

- **Software Detailed Design:** [LoreChatListener_SDD.md](./LoreChatListener_SDD.md)
