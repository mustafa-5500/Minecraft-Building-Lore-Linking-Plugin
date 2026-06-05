# RegionSerializer

> **Software Detailed Documentation:** [RegionSerializer_SDD.md](./RegionSerializer_SDD.md)  
> **Source File:** [RegionSerializer.java](../../src/main/java/org/almond/buildinglore/serializer/RegionSerializer.java)

Converts a [`Selection`](../model/Selection.md) to and from a compact text token for embedding in documents or sharing between players. Uses the format `[BL:world_name|x1,y1,z1>x2,y2,z2|...]` where each pipe-delimited segment after the world name represents a region's min and max corners.

**Functions:**
- [serialize](#serialize)
- [deserialize](#deserialize)

---

## serialize

### Signature
```java
public static String serialize(Selection selection)
```

### Description
Converts a [`Selection`](../model/Selection.md) into a compact text token in the format:
```
[BL:world_name|minX,minY,minZ>maxX,maxY,maxZ|...]
```
Each region is separated by `|`. Designed to be copy-pasted into documents.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `selection` | [`Selection`](../model/Selection.md) | The selection to serialize |

### Returns
`String` — the compact token.

---

## deserialize

### Signature
```java
public static Selection deserialize(String token, UUID owner)
```

### Description
Parses a `[BL:...]` text token back into a [`Selection`](../model/Selection.md) object. The selection is created with the name `"imported"`, a new random UUID, and the current timestamp.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `token` | `String` | The compact token to parse |
| `owner` | `UUID` | The player UUID to assign as owner |

### Returns
[`Selection`](../model/Selection.md) — the reconstructed selection.

### Throws
`IllegalArgumentException` — if the token format is invalid.

## See Also:
- [Selection](../model/Selection.md)