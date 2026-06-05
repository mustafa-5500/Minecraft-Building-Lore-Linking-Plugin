# WandListener

> **Software Detailed Documentation:** [WandListener_SDD.md](./WandListener_SDD.md)  
> **Source File:** [WandListener.java](../../src/main/java/org/almond/buildinglore/listener/WandListener.java)

An event listener that detects when a player interacts with the selection wand and sets selection corners accordingly. Left-click sets corner 1, right-click sets corner 2. Automatically enables particle visualization when the wand is used and shows a volume preview when both corners are set.

**Fields:**
- `selectionManager` — Manages per-player corner state
- `visualizer` — Controls particle-based selection visualization

**Functions:**
- [constructor](#wandlistener-constructor)
- [onPlayerInteract](#onplayerinteract)

---
## WandListener (Constructor)

### Signature
```java
public WandListener(SelectionManager selectionManager)
```

### Description
Creates the listener with a reference to the shared [`SelectionManager`](../manager/SelectionManager.md).

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `selectionManager` | [`SelectionManager`](../manager/SelectionManager.md) | The manager tracking per-player corner state |

---

## onPlayerInteract

### Signature
```java
@EventHandler
public void onPlayerInteract(PlayerInteractEvent event)
```

### Description
Handles `PlayerInteractEvent`. If the player is holding the selection wand and has `buildinglore.use` permission:
- **Left-click block** → sets corner 1 and messages the player
- **Right-click block** → sets corner 2 and messages the player
- If both corners are now set, shows a volume preview

The event is cancelled to prevent the wand from breaking or interacting with the clicked block.

## See Also:
- [Selection](../model/Selection.md)
- [CuboidRegion](../model/CuboidRegion.md)
- [SelectionManager](../manager/SelectionManager.md)
- [Visualizer](../visual/SelectionVisualizer.md)
