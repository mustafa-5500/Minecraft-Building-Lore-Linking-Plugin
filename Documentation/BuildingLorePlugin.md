# [BuildingLorePlugin.java](../src/main/java/org/almond/buildinglore/BuildingLorePlugin.java)

The point of entry for the plugin, where the plugin object is initialized and enabled.

**Functions:**
- [getSelectionManager](#getselectionmanager)
- [getStorageManager](#getstoragemanager)
- [onDisable](#ondisable)
- [onEnable](#onenable)

---

## getSelectionManager

### Signature
```java
public SelectionManager getSelectionManager()
```

### Description
Returns the plugin's `SelectionManager` instance, which tracks per-player wand corner state.

### Parameters
None.

### Returns
`SelectionManager` — the shared selection manager.\
[SelectionManager](./manager/SelectionManager.md)

---

## getStorageManager

### Signature
```java
public SelectionStorageManager getStorageManager()
```

### Description
Returns the plugin's `SelectionStorageManager` instance, which handles persisting and loading selections from disk.

### Parameters
None.

### Returns
`SelectionStorageManager` — the shared storage manager.
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
Called by the server when the plugin is enabled. Initializes the `SelectionManager` and `SelectionStorageManager`, registers the `WandListener` for player interaction events, and binds the `BuildingLoreCommand` as executor and tab completer for the `/bl` command.\
[SelectionManager](./manager/SelectionManager.md)\
[SelectionStorageManager](./manager/SelectionStorageManager.md)\
[WandListener](./listener/WandListener.md)\
[BuildingLoreCommand](./command/BuildingLoreCommand.md)

### Parameters
None.

### Returns
`void`

## See Also:
- [SelectionManager](./manager/SelectionManager.md)
- [SelectionStorageManager](./manager/SelectionStorageManager.md)