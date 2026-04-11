# onPlayerInteract

## Signature
```java
@EventHandler
public void onPlayerInteract(PlayerInteractEvent event)
```

## Description
Handles `PlayerInteractEvent`. If the player is holding the selection wand and has `buildinglore.use` permission:
- **Left-click block** → sets corner 1 and messages the player
- **Right-click block** → sets corner 2 and messages the player
- If both corners are now set, shows a volume preview

The event is cancelled to prevent the wand from breaking or interacting with the clicked block.
