# LoreChatListener — Software Detailed Design

> **API Documentation:** [LoreChatListener.md](./LoreChatListener.md)  
> **Source File:** [LoreChatListener.java](../../src/main/java/org/almond/buildinglore/listener/LoreChatListener.java)

---

## 1. Overview

Listens for chat messages from players who are in lore input mode.
Captures their message as either a document name or lore text entry.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.listener;
```

```java
import org.almond.buildinglore.manager.LoreDocumentManager;
import org.almond.buildinglore.manager.LoreDocumentManager.InputMode;
import org.almond.buildinglore.manager.LoreDocumentManager.InputState;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.almond.buildinglore.model.LoreDocument;
import org.almond.buildinglore.model.Selection;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import java.util.UUID;
```

| Import | Purpose |
|--------|---------|
| [`LoreDocumentManager`](../manager/LoreDocumentManager.md) | TODO: describe purpose |
| `InputMode` | TODO: describe purpose |
| `InputState` | TODO: describe purpose |
| [`SelectionStorageManager`](../manager/SelectionStorageManager.md) | TODO: describe purpose |
| [`LoreDocument`](../model/LoreDocument.md) | TODO: describe purpose |
| [`Selection`](../model/Selection.md) | TODO: describe purpose |
| `ChatColor` | TODO: describe purpose |
| `Player` | TODO: describe purpose |
| `EventHandler` | TODO: describe purpose |
| `EventPriority` | TODO: describe purpose |
| `Listener` | TODO: describe purpose |
| `AsyncPlayerChatEvent` | TODO: describe purpose |
| `UUID` | TODO: describe purpose |

---

## 3. Class Declaration

```java
public class LoreChatListener implements Listener {
```

- **`implements Listener`** — TODO: explain interfaces.

---

## 4. Instance Fields

```java
private static final String PREFIX;
private final LoreDocumentManager loreManager;
private final SelectionStorageManager storageManager;
```

| Field | Type | Description |
|-------|------|-------------|
| `PREFIX` | `String` | TODO: describe |
| `loreManager` | [`LoreDocumentManager`](../manager/LoreDocumentManager.md) | TODO: describe |
| `storageManager` | [`SelectionStorageManager`](../manager/SelectionStorageManager.md) | TODO: describe |

---

## 5. Constructor

```java
public LoreChatListener(LoreDocumentManager loreManager, SelectionStorageManager storageManager)
```

TODO: Provide detailed design explanation for `LoreChatListener`.

---

## 6. `onChat()`

```java
@EventHandler(priority = EventPriority.LOWEST)
public void onChat(AsyncPlayerChatEvent event)
```

TODO: Provide detailed design explanation for `onChat`.

---

## 7. `handleNaming()`

```java
private void handleNaming(Player player, InputState state, String name)
```

TODO: Provide detailed design explanation for `handleNaming`.

---

## 8. `handleWriting()`

```java
private void handleWriting(Player player, InputState state, String text)
```

TODO: Provide detailed design explanation for `handleWriting`.

---
