package org.almond.buildinglore.util;

import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.List;

/**
 * Helper to create and detect the selection wand item.
 */
public class WandUtil {

    private static final String WAND_NAME = ChatColor.GOLD + "Selection Wand";
    private static final Material WAND_MATERIAL = Material.WOODEN_AXE;

    /** Create a wand ItemStack */
    public static ItemStack createWand() {
        ItemStack wand = new ItemStack(WAND_MATERIAL);
        ItemMeta meta = wand.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(WAND_NAME);
            meta.setLore(List.of(
                ChatColor.GRAY + "Left-click: set corner 1",
                ChatColor.GRAY + "Right-click: set corner 2"
            ));
            wand.setItemMeta(meta);
        }
        return wand;
    }

    /** Check if an ItemStack is the selection wand */
    public static boolean isWand(ItemStack item) {
        if (item == null || item.getType() != WAND_MATERIAL) return false;
        ItemMeta meta = item.getItemMeta();
        return meta != null && WAND_NAME.equals(meta.getDisplayName());
    }
}
