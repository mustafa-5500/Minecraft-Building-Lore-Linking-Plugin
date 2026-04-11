# deserialize

## Signature
```java
public static Selection deserialize(String token, UUID owner)
```

## Description
Parses a `[BL:...]` text token back into a `Selection` object. The selection is created with the name `"imported"`, a new random UUID, and the current timestamp.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `token` | `String` | The compact token to parse |
| `owner` | `UUID` | The player UUID to assign as owner |

## Returns
`Selection` — the reconstructed selection.

## Throws
`IllegalArgumentException` — if the token format is invalid.
