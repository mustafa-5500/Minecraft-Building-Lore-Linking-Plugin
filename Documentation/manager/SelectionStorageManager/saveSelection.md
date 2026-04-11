# saveSelection

## Signature
```java
public void saveSelection(Selection selection)
```

## Description
Persists a selection to disk as a YAML file at `selections/<owner-uuid>/<name>.yml`. Also updates the in-memory cache. Region data is stored as compact string representations.

## Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to save |

## Returns
`void`
