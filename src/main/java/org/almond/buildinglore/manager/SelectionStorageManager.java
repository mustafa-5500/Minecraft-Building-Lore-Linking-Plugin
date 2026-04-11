package org.almond.buildinglore.manager;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.logging.Level;

import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.Selection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Persists Selections as YAML files under plugins/BuildingLore/selections/<player-uuid>/.
 */
public class SelectionStorageManager {

    private final File selectionsDir;
    private final JavaPlugin plugin;
    // In-memory cache: owner UUID -> (selection name -> Selection)
    private final Map<UUID, Map<String, Selection>> cache = new HashMap<>();

    public SelectionStorageManager(JavaPlugin plugin) {
        this.plugin = plugin;
        this.selectionsDir = new File(plugin.getDataFolder(), "selections");
        if (!selectionsDir.exists()) {
            selectionsDir.mkdirs();
        }
    }

    /** Save a selection to disk and update cache */
    public void saveSelection(Selection selection) {
        File playerDir = new File(selectionsDir, selection.getOwner().toString());
        if (!playerDir.exists()) {
            playerDir.mkdirs();
        }
        File file = new File(playerDir, selection.getName() + ".yml");
        YamlConfiguration config = new YamlConfiguration();
        config.set("id", selection.getId().toString());
        config.set("name", selection.getName());
        config.set("owner", selection.getOwner().toString());
        config.set("world", selection.getWorldName());
        config.set("createdAt", selection.getCreatedAt());

        List<String> regionStrings = new ArrayList<>();
        for (CuboidRegion region : selection.getRegions()) {
            regionStrings.add(region.toString());
        }
        config.set("regions", regionStrings);

        try {
            config.save(file);
        } catch (IOException e) {
            plugin.getLogger().log(Level.SEVERE, "Failed to save selection " + selection.getName(), e);
        }

        // Update cache
        cache.computeIfAbsent(selection.getOwner(), k -> new HashMap<>()).put(selection.getName(), selection);
    }

    /** Load a single selection from disk */
    public Selection loadSelection(UUID owner, String name) {
        // Check cache first
        Map<String, Selection> playerCache = cache.get(owner);
        if (playerCache != null && playerCache.containsKey(name)) {
            return playerCache.get(name);
        }

        File file = new File(selectionsDir, owner.toString() + File.separator + name + ".yml");
        if (!file.exists()) return null;

        return loadFromFile(file, owner);
    }

    /** Load all selections for a player */
    public List<Selection> loadAllForPlayer(UUID owner) {
        // Check if already cached completely
        Map<String, Selection> playerCache = cache.get(owner);
        if (playerCache != null && !playerCache.isEmpty()) {
            return new ArrayList<>(playerCache.values());
        }

        List<Selection> result = new ArrayList<>();
        File playerDir = new File(selectionsDir, owner.toString());
        if (!playerDir.exists() || !playerDir.isDirectory()) return result;

        File[] files = playerDir.listFiles((dir, fileName) -> fileName.endsWith(".yml"));
        if (files == null) return result;

        for (File file : files) {
            Selection sel = loadFromFile(file, owner);
            if (sel != null) {
                result.add(sel);
            }
        }
        return result;
    }

    /** Delete a selection from disk and cache */
    public boolean deleteSelection(UUID owner, String name) {
        File file = new File(selectionsDir, owner.toString() + File.separator + name + ".yml");
        boolean deleted = file.exists() && file.delete();

        Map<String, Selection> playerCache = cache.get(owner);
        if (playerCache != null) {
            playerCache.remove(name);
        }
        return deleted;
    }

    /** Get a selection from cache or load it */
    public Selection getSelection(UUID owner, String name) {
        return loadSelection(owner, name);
    }

    private Selection loadFromFile(File file, UUID owner) {
        YamlConfiguration config = YamlConfiguration.loadConfiguration(file);
        try {
            UUID id = UUID.fromString(config.getString("id"));
            String name = config.getString("name");
            String world = config.getString("world");
            long createdAt = config.getLong("createdAt");

            List<CuboidRegion> regions = new ArrayList<>();
            List<String> regionStrings = config.getStringList("regions");
            for (String regionStr : regionStrings) {
                regions.add(CuboidRegion.fromString(world, regionStr));
            }

            Selection selection = new Selection(id, name, owner, world, regions, createdAt);
            cache.computeIfAbsent(owner, k -> new HashMap<>()).put(name, selection);
            return selection;
        } catch (Exception e) {
            plugin.getLogger().log(Level.WARNING, "Failed to load selection from " + file.getName(), e);
            return null;
        }
    }
}
