# buildRegion

## Signature
```java
public CuboidRegion buildRegion(UUID playerId)
```

## Description
Creates a `CuboidRegion` from the player's two stored corners, then clears the corner state. Returns `null` if the selection is incomplete.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `playerId` | `UUID` | The player's unique ID |

## Returns
`CuboidRegion` or `null` — the constructed region, or `null` if corners are not ready.
