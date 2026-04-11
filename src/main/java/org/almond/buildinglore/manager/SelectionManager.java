package org.almond.buildinglore.manager;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.almond.buildinglore.model.CuboidRegion;
import org.bukkit.Location;

/**
 * Per-player ephemeral state for building cuboid regions with a wand.
 * Adapted from org.almond.lands.manager.SelectionManager.
 */
public class SelectionManager {

    private final Map<UUID, Location> corner1 = new HashMap<>();
    private final Map<UUID, Location> corner2 = new HashMap<>();

    public void setCorner1(UUID playerId, Location location) {
        corner1.put(playerId, location);
    }

    public void setCorner2(UUID playerId, Location location) {
        corner2.put(playerId, location);
    }

    public Location getCorner1(UUID playerId) {
        return corner1.get(playerId);
    }

    public Location getCorner2(UUID playerId) {
        return corner2.get(playerId);
    }

    /** Both corners are set and in the same world */
    public boolean hasCompleteSelection(UUID playerId) {
        Location c1 = corner1.get(playerId);
        Location c2 = corner2.get(playerId);
        if (c1 == null || c2 == null) return false;
        if (c1.getWorld() == null || c2.getWorld() == null) return false;
        return c1.getWorld().equals(c2.getWorld());
    }

    /** Build a CuboidRegion from the two corners, then clear them */
    public CuboidRegion buildRegion(UUID playerId) {
        if (!hasCompleteSelection(playerId)) return null;
        Location c1 = corner1.get(playerId);
        Location c2 = corner2.get(playerId);
        CuboidRegion region = new CuboidRegion(
            c1.getWorld().getName(),
            c1.getBlockX(), c1.getBlockY(), c1.getBlockZ(),
            c2.getBlockX(), c2.getBlockY(), c2.getBlockZ()
        );
        clearSelection(playerId);
        return region;
    }

    /** Peek at what the region would be without consuming the corners */
    public CuboidRegion peekRegion(UUID playerId) {
        if (!hasCompleteSelection(playerId)) return null;
        Location c1 = corner1.get(playerId);
        Location c2 = corner2.get(playerId);
        return new CuboidRegion(
            c1.getWorld().getName(),
            c1.getBlockX(), c1.getBlockY(), c1.getBlockZ(),
            c2.getBlockX(), c2.getBlockY(), c2.getBlockZ()
        );
    }

    public void clearSelection(UUID playerId) {
        corner1.remove(playerId);
        corner2.remove(playerId);
    }
}
