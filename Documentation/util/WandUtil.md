# WandUtil.java
[[WandUtil.java]]

Helper utility for creating and detecting the selection wand item. The wand is a wooden axe with a distinctive display name and lore text, used to set selection corners via left/right clicks.

**Constants:**
- `WAND_NAME` — Display name for the wand (`"Selection Wand"` in gold)
- `WAND_MATERIAL` — The material type (`WOODEN_AXE`)

**Functions:**
[[createWand]]
[[isWand]]

---

## createWand

### Signature
```java
public static ItemStack createWand()
```

### Description
Creates a selection wand `ItemStack` — a wooden axe with the display name "Selection Wand" (gold text) and lore explaining left/right click usage.

### Parameters
None.

### Returns
`ItemStack` — the wand item.

---

## isWand

### Signature
```java
public static boolean isWand(ItemStack item)
```

### Description
Checks if an `ItemStack` is the selection wand by verifying the material type (wooden axe) and display name match.

### Parameters
| Name | Type | Description |
|------|------|-------------|
| `item` | `ItemStack` | The item to check (may be `null`) |

### Returns
`boolean` — `true` if the item is the selection wand.
