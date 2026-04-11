# loadFromFile

## Signature
```java
private Selection loadFromFile(File file, UUID owner)
```

## Description
Internal method that reads a YAML file and reconstructs a `Selection` object. Parses the id, name, world, timestamp, and region strings. Caches the result. Logs a warning on failure.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `file` | `File` | The YAML file to read |
| `owner` | `UUID` | The owning player's UUID |

## Returns
`Selection` or `null` — the parsed selection, or `null` if parsing failed.
