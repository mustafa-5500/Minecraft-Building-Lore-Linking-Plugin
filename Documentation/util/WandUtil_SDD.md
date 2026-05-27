# WandUtil — Software Detailed Design

> **API Documentation:** [WandUtil.md](./WandUtil.md)  
> **Source File:** [WandUtil.java](../../src/main/java/org/almond/buildinglore/util/WandUtil.java)

---

## 1. Overview

`WandUtil` is a utility class that encapsulates the creation and detection of the BuildingLore selection wand item. The wand is a `WOODEN_AXE` with a specific display name and lore text, used to identify it uniquely from regular wooden axes.

---

## 2. Package Declaration & Imports

```java
package org.almond.buildinglore.util;
```

```java
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.List;
```

| Import | Purpose |
|--------|---------|
| `ChatColor` | Color codes for the wand name and lore text |
| `Material` | Enum of all Minecraft item/block types |
| `ItemStack` | Represents a stack of items in an inventory |
| `ItemMeta` | Interface for item metadata (name, lore, enchantments, etc.) |
| `List` | Used for `List.of(...)` to create the lore lines |

---

## 3. Class Declaration

```java
/**
 * Helper to create and detect the selection wand item.
 */
public class WandUtil {
```

Utility class with only `static` members — never instantiated.

---

## 4. Constants

```java
private static final String WAND_NAME = ChatColor.GOLD + "Selection Wand";
private static final Material WAND_MATERIAL = Material.WOODEN_AXE;
```

| Constant | Value | Purpose |
|----------|-------|---------|
| `WAND_NAME` | `"§6Selection Wand"` | The exact display name used for identification. `ChatColor.GOLD` prepends `§6`. |
| `WAND_MATERIAL` | `WOODEN_AXE` | The base material chosen for the wand item. |

These are `private` — external code should use `createWand()` and `isWand()` rather than checking these directly. The `WAND_NAME` includes the color code prefix, which becomes part of the string comparison in `isWand()`.

---

## 5. `createWand()` — Wand Construction

```java
public static ItemStack createWand() {
    ItemStack wand = new ItemStack(WAND_MATERIAL);
```

Creates a new `ItemStack` of type `WOODEN_AXE` with stack size 1 (default).

```java
    ItemMeta meta = wand.getItemMeta();
```

Retrieves the `ItemMeta` instance for this item. For a fresh `ItemStack`, this returns a default meta with no custom name or lore.

```java
    if (meta != null) {
```

Null-check: `getItemMeta()` can theoretically return `null` for items without a meta type, though this is extremely rare for standard materials.

```java
        meta.setDisplayName(WAND_NAME);
```

Sets the custom display name to `"§6Selection Wand"`. This renders in gold text in the player's inventory and hotbar.

```java
        meta.setLore(List.of(
            ChatColor.GRAY + "Left-click: set corner 1",
            ChatColor.GRAY + "Right-click: set corner 2"
        ));
```

Sets the item lore (tooltip text below the name) to two gray lines explaining the wand's usage. `List.of(...)` creates an immutable list.

```java
        wand.setItemMeta(meta);
    }
    return wand;
}
```

Applies the modified meta back to the item stack and returns it.

---

## 6. `isWand(ItemStack)` — Wand Detection

```java
public static boolean isWand(ItemStack item) {
    if (item == null || item.getType() != WAND_MATERIAL) return false;
```

First-level filter:
- `null` check for empty hand slots.
- Material check — must be `WOODEN_AXE`. This is a fast O(1) check that rejects 99% of items immediately.

```java
    ItemMeta meta = item.getItemMeta();
    return meta != null && WAND_NAME.equals(meta.getDisplayName());
}
```

Second-level filter:
- Meta must exist.
- Display name must exactly match `WAND_NAME` (including the `§6` color code prefix).

This means a regular wooden axe (no custom name) will **not** be identified as the wand. Only items explicitly created by `createWand()` (or manually renamed to exactly `"§6Selection Wand"`) will match.

---

## 7. Identification Mechanism

The wand is identified purely by **material + display name** combination. This approach:

| Pro | Con |
|-----|-----|
| Simple to implement | Players could theoretically craft a matching item with an anvil |
| No persistent data needed | Doesn't survive item serialization edge cases (unlikely) |
| Works across server restarts | Relies on exact string match including color codes |

Alternative approaches not used:
- **NBT tags / PersistentDataContainer** — more robust but adds complexity.
- **Custom model data** — overkill for a utility item.
- **Unique enchantment** — would show enchantment glint.

---

## 8. Usage in the Codebase

| Caller | Method Used | Context |
|--------|-------------|---------|
| `WandListener.onPlayerInteract` | `isWand(...)` | Check if player's main hand item is the wand |
| `BuildingLoreCommand.handleWand` | `createWand()` | Give the player a wand item |

---

## 9. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Static utility class | No state; pure factory/predicate functions |
| `WOODEN_AXE` as base material | Matches WorldEdit convention; players expect axes for selection tools |
| Color code in name | Visually distinguishes from regular items; part of identity check |
| `private` constants | External code should use the public methods, not raw values |
| `WAND_NAME.equals(meta.getDisplayName())` | Null-safe: `WAND_NAME` is never null, so calling `.equals` on it handles `getDisplayName()` returning null |
| Lore text purely informational | Does not participate in identification; only for player UX |
