# loadSelection

## Signature
```java
public Selection loadSelection(UUID owner, String name)
```

## Description
Loads a single selection by owner and name. Checks the in-memory cache first; if not cached, reads from disk.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |
| `name` | `String` | Selection name |

## Returns
`Selection` or `null` — the loaded selection, or `null` if not found.
