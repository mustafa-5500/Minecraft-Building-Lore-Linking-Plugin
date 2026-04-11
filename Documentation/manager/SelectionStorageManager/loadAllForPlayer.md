# loadAllForPlayer

## Signature
```java
public List<Selection> loadAllForPlayer(UUID owner)
```

## Description
Loads all saved selections for a player. Returns from cache if available, otherwise reads all `.yml` files in the player's selection directory.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |

## Returns
`List<Selection>` — all selections belonging to the player (empty list if none).
