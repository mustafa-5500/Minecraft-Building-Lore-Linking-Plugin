# getSelection

## Signature
```java
public Selection getSelection(UUID owner, String name)
```

## Description
Convenience method that delegates to `loadSelection`. Returns a selection from cache or disk.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |
| `name` | `String` | Selection name |

## Returns
`Selection` or `null`.
