# RegionSerializer.java
[[RegionSerializer.java]]

Converts a `Selection` to and from a compact text token for embedding in documents or sharing between players. Uses the format `[BL:world_name|x1,y1,z1>x2,y2,z2|...]` where each pipe-delimited segment after the world name represents a region's min and max corners.

**Functions:**
[[serialize]]
[[deserialize]]

---

## serialize

### Signature
```java
public static String serialize(Selection selection)
```

### Description
Converts a `Selection` into a compact text token in the format:
```
[BL:world_name|minX,minY,minZ>maxX,maxY,maxZ|...]
```
Each region is separated by `|`. Designed to be copy-pasted into documents.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | `Selection` | The selection to serialize |

### Returns
`String` — the compact token.

---

## deserialize

### Signature
```java
public static Selection deserialize(String token, UUID owner)
```

### Description
Parses a `[BL:...]` text token back into a `Selection` object. The selection is created with the name `"imported"`, a new random UUID, and the current timestamp.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `token` | `String` | The compact token to parse |
| `owner` | `UUID` | The player UUID to assign as owner |

### Returns
`Selection` — the reconstructed selection.

### Throws
`IllegalArgumentException` — if the token format is invalid.
