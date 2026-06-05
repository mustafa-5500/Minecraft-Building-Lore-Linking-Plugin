# BuildingLorePlugin

> **Software Detailed Documentation:** [BuildingLorePlugin_SDD.md](./BuildingLorePlugin_SDD.md)  
> **Source File:** [BuildingLorePlugin.java](../src/main/java/org/almond/buildinglore/BuildingLorePlugin.java)

The point of entry for the plugin, where the plugin object is initialized and enabled.

**Functions:**
- [getSelectionManager](#getselectionmanager)
- [getStorageManager](#getstoragemanager)
- [onDisable](#ondisable)
- [onEnable](#onenable)
- [getVisualizer](#getvisualizer)
- [getLoreManager](#getloremanager)

---

## getSelectionManager

### Signature
```java
public SelectionManager getSelectionManager()
```

### Description
Returns the plugin's [`SelectionManager`](manager/SelectionManager.md) instance, which tracks per-player wand corner state.

### Parameters
None.

### Returns
[`SelectionManager`](manager/SelectionManager.md) — the shared selection manager.\
[SelectionManager](./manager/SelectionManager.md)

---

## getStorageManager

### Signature
```java
public SelectionStorageManager getStorageManager()
```

### Description
Returns the plugin's [`SelectionStorageManager`](manager/SelectionStorageManager.md) instance, which handles persisting and loading selections from disk.

### Parameters
None.

### Returns
[`SelectionStorageManager`](manager/SelectionStorageManager.md) — the shared storage manager.
[SelectionStorageManager](./manager/SelectionStorageManager.md)

---

## onDisable

### Signature
```java
@Override
public void onDisable()
```

### Description
Called by the server when the plugin is disabled. Logs a shutdown message.

### Parameters
None.

### Returns
`void`

---

## onEnable

### Signature
```java
@Override
public void onEnable()
```

### Description
Called by the server when the plugin is enabled. Initializes the [`SelectionManager`](manager/SelectionManager.md) and [`SelectionStorageManager`](manager/SelectionStorageManager.md), registers the [`WandListener`](listener/WandListener.md) for player interaction events, and binds the [`BuildingLoreCommand`](command/BuildingLoreCommand.md) as executor and tab completer for the `/bl` command.\
[SelectionManager](./manager/SelectionManager.md)\
[SelectionStorageManager](./manager/SelectionStorageManager.md)\
[WandListener](./listener/WandListener.md)\
[BuildingLoreCommand](./command/BuildingLoreCommand.md)

### Parameters
None.

### Returns
`void`

## getVisualizer

### Signature
```java
public SelectionVisualizer getVisualizer()
```

### Description
TODO: Describe what `getVisualizer` does.

### Parameters
None.

### Returns
[`SelectionVisualizer`](visual/SelectionVisualizer.md) — TODO: describe return value.

---

## getLoreManager

### Signature
```java
public LoreDocumentManager getLoreManager()
```

### Description
TODO: Describe what `getLoreManager` does.

### Parameters
None.

### Returns
[`LoreDocumentManager`](manager/LoreDocumentManager.md) — TODO: describe return value.

---

## See Also:
- [SelectionManager](./manager/SelectionManager.md)
- [SelectionStorageManager](./manager/SelectionStorageManager.md)