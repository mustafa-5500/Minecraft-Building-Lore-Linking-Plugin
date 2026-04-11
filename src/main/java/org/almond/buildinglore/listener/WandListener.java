package org.almond.buildinglore.listener;

import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.util.WandUtil;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;

/**
 * Listens for wand clicks to set selection corners.
 */
public class WandListener implements Listener {

    private final SelectionManager selectionManager;

    public WandListener(SelectionManager selectionManager) {
        this.selectionManager = selectionManager;
    }

    @EventHandler
    public void onPlayerInteract(PlayerInteractEvent event) {
        Player player = event.getPlayer();

        if (!WandUtil.isWand(player.getInventory().getItemInMainHand())) return;
        if (!player.hasPermission("buildinglore.use")) return;

        Block block = event.getClickedBlock();
        if (block == null) return;

        Location loc = block.getLocation();

        if (event.getAction() == Action.LEFT_CLICK_BLOCK) {
            selectionManager.setCorner1(player.getUniqueId(), loc);
            player.sendMessage(ChatColor.YELLOW + "Corner 1 set: " +
                ChatColor.WHITE + loc.getBlockX() + ", " + loc.getBlockY() + ", " + loc.getBlockZ());
            event.setCancelled(true);
        } else if (event.getAction() == Action.RIGHT_CLICK_BLOCK) {
            selectionManager.setCorner2(player.getUniqueId(), loc);
            player.sendMessage(ChatColor.YELLOW + "Corner 2 set: " +
                ChatColor.WHITE + loc.getBlockX() + ", " + loc.getBlockY() + ", " + loc.getBlockZ());
            event.setCancelled(true);
        }

        // Show volume preview if both corners are set
        if (selectionManager.hasCompleteSelection(player.getUniqueId())) {
            var preview = selectionManager.peekRegion(player.getUniqueId());
            if (preview != null) {
                player.sendMessage(ChatColor.GRAY + "Selection volume: " + ChatColor.WHITE + preview.getVolume() + " blocks");
            }
        }
    }
}
