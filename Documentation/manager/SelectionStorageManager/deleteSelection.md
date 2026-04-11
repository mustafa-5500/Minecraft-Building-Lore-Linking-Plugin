# deleteSelection

## Signature
```java
public boolean deleteSelection(UUID owner, String name)
```

## Description
Deletes a selection's YAML file from disk and removes it from the in-memory cache.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `owner` | `UUID` | Player UUID |
| `name` | `String` | Selection name |

## Returns
`boolean` — `true` if the file existed and was deleted.
