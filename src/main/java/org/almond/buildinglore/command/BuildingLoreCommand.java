package org.almond.buildinglore.command;

import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.Selection;
import org.almond.buildinglore.serializer.BlockDataExporter;
import org.almond.buildinglore.serializer.RegionSerializer;
import org.almond.buildinglore.util.WandUtil;
import org.bukkit.ChatColor;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabExecutor;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Command tree for /bl.
 */
public class BuildingLoreCommand implements TabExecutor {

    private final JavaPlugin plugin;
    private final SelectionManager selectionManager;
    private final SelectionStorageManager storageManager;

    private static final String PREFIX = ChatColor.DARK_AQUA + "[BuildingLore] " + ChatColor.RESET;

    public BuildingLoreCommand(JavaPlugin plugin, SelectionManager selectionManager, SelectionStorageManager storageManager) {
        this.plugin = plugin;
        this.selectionManager = selectionManager;
        this.storageManager = storageManager;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("This command can only be used by players.");
            return true;
        }

        if (args.length == 0) {
            sendHelp(player);
            return true;
        }

        String sub = args[0].toLowerCase();

        switch (sub) {
            case "wand" -> handleWand(player);
            case "pos1" -> handlePos1(player);
            case "pos2" -> handlePos2(player);
            case "add" -> handleAdd(player, args);
            case "remove" -> handleRemove(player, args);
            case "list" -> handleList(player);
            case "info" -> handleInfo(player, args);
            case "delete" -> handleDelete(player, args);
            case "serialize" -> handleSerialize(player, args);
            case "export" -> handleExport(player, args);
            case "import" -> handleImport(player, args);
            default -> sendHelp(player);
        }
        return true;
    }

    // ---- Subcommand handlers ----

    private void handleWand(Player player) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        player.getInventory().addItem(WandUtil.createWand());
        player.sendMessage(PREFIX + "Selection wand given. Left-click to set corner 1, right-click for corner 2.");
    }

    private void handlePos1(Player player) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        selectionManager.setCorner1(player.getUniqueId(), player.getLocation());
        player.sendMessage(PREFIX + ChatColor.YELLOW + "Corner 1 set to your position.");
        showPreview(player);
    }

    private void handlePos2(Player player) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        selectionManager.setCorner2(player.getUniqueId(), player.getLocation());
        player.sendMessage(PREFIX + ChatColor.YELLOW + "Corner 2 set to your position.");
        showPreview(player);
    }

    private void handleAdd(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        if (args.length < 2) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl add <name>");
            return;
        }
        if (!selectionManager.hasCompleteSelection(player.getUniqueId())) {
            player.sendMessage(PREFIX + ChatColor.RED + "Set both corners first (wand or /bl pos1 & /bl pos2).");
            return;
        }

        String name = args[1];
        CuboidRegion region = selectionManager.buildRegion(player.getUniqueId());
        if (region == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Failed to create region.");
            return;
        }

        // Load or create the selection
        Selection selection = storageManager.getSelection(player.getUniqueId(), name);
        if (selection == null) {
            selection = new Selection(name, player.getUniqueId(), region.getWorldName());
        }
        selection.addRegion(region);
        storageManager.saveSelection(selection);

        player.sendMessage(PREFIX + "Region added to " + ChatColor.GREEN + name +
            ChatColor.RESET + ". Total regions: " + selection.getRegionCount() +
            ", Volume: " + selection.getTotalVolume() + " blocks.");
    }

    private void handleRemove(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        if (args.length < 3) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl remove <name> <index>");
            return;
        }
        String name = args[1];
        int index;
        try {
            index = Integer.parseInt(args[2]);
        } catch (NumberFormatException e) {
            player.sendMessage(PREFIX + ChatColor.RED + "Index must be a number.");
            return;
        }

        Selection selection = storageManager.getSelection(player.getUniqueId(), name);
        if (selection == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + name + "' not found.");
            return;
        }
        if (!selection.removeRegion(index)) {
            player.sendMessage(PREFIX + ChatColor.RED + "Invalid region index. Use /bl info " + name + " to see indices.");
            return;
        }
        storageManager.saveSelection(selection);
        player.sendMessage(PREFIX + "Region " + index + " removed from " + ChatColor.GREEN + name + ChatColor.RESET + ".");
    }

    private void handleList(Player player) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        List<Selection> selections = storageManager.loadAllForPlayer(player.getUniqueId());
        if (selections.isEmpty()) {
            player.sendMessage(PREFIX + "You have no saved selections.");
            return;
        }
        player.sendMessage(PREFIX + ChatColor.AQUA + "Your Selections:");
        for (Selection sel : selections) {
            player.sendMessage(ChatColor.GREEN + "  " + sel.getName() +
                ChatColor.GRAY + " — " + sel.getRegionCount() + " regions, " +
                sel.getTotalVolume() + " blocks (" + sel.getWorldName() + ")");
        }
    }

    private void handleInfo(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        if (args.length < 2) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl info <name>");
            return;
        }
        String name = args[1];
        Selection selection = storageManager.getSelection(player.getUniqueId(), name);
        if (selection == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + name + "' not found.");
            return;
        }
        player.sendMessage(PREFIX + ChatColor.AQUA + "Selection: " + ChatColor.GREEN + selection.getName());
        player.sendMessage(ChatColor.GRAY + "  World: " + selection.getWorldName());
        player.sendMessage(ChatColor.GRAY + "  Total Volume: " + selection.getTotalVolume() + " blocks");
        player.sendMessage(ChatColor.GRAY + "  Regions (" + selection.getRegionCount() + "):");
        List<CuboidRegion> regions = selection.getRegions();
        for (int i = 0; i < regions.size(); i++) {
            CuboidRegion r = regions.get(i);
            player.sendMessage(ChatColor.WHITE + "    [" + i + "] " + r.toString() + ChatColor.GRAY + " (" + r.getVolume() + " blocks)");
        }
    }

    private void handleDelete(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        if (args.length < 2) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl delete <name>");
            return;
        }
        String name = args[1];
        if (storageManager.deleteSelection(player.getUniqueId(), name)) {
            player.sendMessage(PREFIX + "Selection " + ChatColor.GREEN + name + ChatColor.RESET + " deleted.");
        } else {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + name + "' not found.");
        }
    }

    private void handleSerialize(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        if (args.length < 2) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl serialize <name>");
            return;
        }
        String name = args[1];
        Selection selection = storageManager.getSelection(player.getUniqueId(), name);
        if (selection == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + name + "' not found.");
            return;
        }
        String token = RegionSerializer.serialize(selection);
        player.sendMessage(PREFIX + "Serialized token:");
        player.sendMessage(ChatColor.WHITE + token);
    }

    private void handleExport(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.export")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission to export.");
            return;
        }
        if (args.length < 2) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl export <name>");
            return;
        }
        String name = args[1];
        Selection selection = storageManager.getSelection(player.getUniqueId(), name);
        if (selection == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + name + "' not found.");
            return;
        }
        World world = plugin.getServer().getWorld(selection.getWorldName());
        if (world == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "World '" + selection.getWorldName() + "' is not loaded.");
            return;
        }

        player.sendMessage(PREFIX + "Exporting block data for '" + name + "'... (this may take a moment)");

        // Run async-safe: reading blocks must happen on the main thread, so we do it synchronously
        // but warn the player. For very large selections, a future improvement would be chunked async.
        try {
            File exportDir = new File(plugin.getDataFolder(), "exports" + File.separator + player.getUniqueId());
            File outputFile = BlockDataExporter.exportToFile(selection, world, exportDir, true);
            player.sendMessage(PREFIX + ChatColor.GREEN + "Exported to: " + outputFile.getPath());
        } catch (Exception e) {
            player.sendMessage(PREFIX + ChatColor.RED + "Export failed: " + e.getMessage());
            plugin.getLogger().warning("Export failed for " + name + ": " + e.getMessage());
        }
    }

    private void handleImport(Player player, String[] args) {
        if (!player.hasPermission("buildinglore.use")) {
            player.sendMessage(PREFIX + ChatColor.RED + "No permission.");
            return;
        }
        if (args.length < 2) {
            player.sendMessage(PREFIX + ChatColor.RED + "Usage: /bl import <token>");
            return;
        }
        // Rejoin args in case the token had spaces (shouldn't, but safety)
        String token = String.join(" ", java.util.Arrays.copyOfRange(args, 1, args.length));
        try {
            Selection selection = RegionSerializer.deserialize(token, player.getUniqueId());
            storageManager.saveSelection(selection);
            player.sendMessage(PREFIX + "Imported selection with " + selection.getRegionCount() +
                " regions in world '" + selection.getWorldName() + "'.");
            player.sendMessage(PREFIX + "Saved as: " + ChatColor.GREEN + selection.getName() +
                ChatColor.RESET + ". Use /bl list to see it, /bl info imported to view details.");
        } catch (IllegalArgumentException e) {
            player.sendMessage(PREFIX + ChatColor.RED + "Invalid token: " + e.getMessage());
        }
    }

    // ---- Helpers ----

    private void showPreview(Player player) {
        if (selectionManager.hasCompleteSelection(player.getUniqueId())) {
            CuboidRegion preview = selectionManager.peekRegion(player.getUniqueId());
            if (preview != null) {
                player.sendMessage(PREFIX + ChatColor.GRAY + "Selection: " + preview.toString() +
                    " (" + preview.getVolume() + " blocks)");
            }
        }
    }

    private void sendHelp(Player player) {
        player.sendMessage(PREFIX + ChatColor.AQUA + "Building Lore Commands:");
        player.sendMessage(ChatColor.YELLOW + "  /bl wand" + ChatColor.GRAY + " — Get the selection wand");
        player.sendMessage(ChatColor.YELLOW + "  /bl pos1" + ChatColor.GRAY + " — Set corner 1 at your feet");
        player.sendMessage(ChatColor.YELLOW + "  /bl pos2" + ChatColor.GRAY + " — Set corner 2 at your feet");
        player.sendMessage(ChatColor.YELLOW + "  /bl add <name>" + ChatColor.GRAY + " — Add current region to a selection");
        player.sendMessage(ChatColor.YELLOW + "  /bl remove <name> <index>" + ChatColor.GRAY + " — Remove a region by index");
        player.sendMessage(ChatColor.YELLOW + "  /bl list" + ChatColor.GRAY + " — List your selections");
        player.sendMessage(ChatColor.YELLOW + "  /bl info <name>" + ChatColor.GRAY + " — Show selection details");
        player.sendMessage(ChatColor.YELLOW + "  /bl delete <name>" + ChatColor.GRAY + " — Delete a selection");
        player.sendMessage(ChatColor.YELLOW + "  /bl serialize <name>" + ChatColor.GRAY + " — Get a text token for a selection");
        player.sendMessage(ChatColor.YELLOW + "  /bl export <name>" + ChatColor.GRAY + " — Export block data to file");
        player.sendMessage(ChatColor.YELLOW + "  /bl import <token>" + ChatColor.GRAY + " — Import a selection from a token");
    }

    // ---- Tab completion ----

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (!(sender instanceof Player player)) return Collections.emptyList();

        if (args.length == 1) {
            List<String> subs = List.of("wand", "pos1", "pos2", "add", "remove", "list", "info", "delete", "serialize", "export", "import");
            return subs.stream()
                .filter(s -> s.startsWith(args[0].toLowerCase()))
                .collect(Collectors.toList());
        }

        if (args.length == 2) {
            String sub = args[0].toLowerCase();
            if (List.of("add", "remove", "info", "delete", "serialize", "export").contains(sub)) {
                // Suggest selection names
                return storageManager.loadAllForPlayer(player.getUniqueId()).stream()
                    .map(Selection::getName)
                    .filter(n -> n.toLowerCase().startsWith(args[1].toLowerCase()))
                    .collect(Collectors.toList());
            }
        }

        return Collections.emptyList();
    }
}
