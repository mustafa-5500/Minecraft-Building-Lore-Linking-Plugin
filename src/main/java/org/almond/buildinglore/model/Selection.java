package org.almond.buildinglore.model;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * A named set of CuboidRegions belonging to a player.
 * Adapted from org.almond.lands.model.Land (stripped of permissions/roles).
 */
public class Selection {
    private final UUID id;
    private final String name;
    private final UUID owner;
    private final String worldName;
    private final List<CuboidRegion> regions;
    private final long createdAt;

    public Selection(UUID id, String name, UUID owner, String worldName, List<CuboidRegion> regions, long createdAt) {
        this.id = id;
        this.name = name;
        this.owner = owner;
        this.worldName = worldName;
        this.regions = new ArrayList<>(regions);
        this.createdAt = createdAt;
    }

    /** Convenience constructor — generates a new UUID and timestamp */
    public Selection(String name, UUID owner, String worldName) {
        this(UUID.randomUUID(), name, owner, worldName, new ArrayList<>(), System.currentTimeMillis());
    }

    /** Add a region to this selection */
    public void addRegion(CuboidRegion region) {
        regions.add(region);
    }

    /** Remove a region by index (0-based) */
    public boolean removeRegion(int index) {
        if (index < 0 || index >= regions.size()) return false;
        regions.remove(index);
        return true;
    }

    /** Total block count across all regions (no overlap dedup) */
    public long getTotalVolume() {
        long total = 0;
        for (CuboidRegion region : regions) {
            total += region.getVolume();
        }
        return total;
    }

    /** Check if any region in this selection contains the given block */
    public boolean containsBlock(int x, int y, int z) {
        for (CuboidRegion region : regions) {
            if (region.contains(x, y, z)) return true;
        }
        return false;
    }

    /** Merge adjacent, same-plane regions to optimize the set */
    public void mergeRegions() {
        List<CuboidRegion> merged = new ArrayList<>();
        for (CuboidRegion region : this.regions) {
            boolean wasMerged = false;
            for (int i = 0; i < merged.size(); i++) {
                CuboidRegion existing = merged.get(i);
                if (existing.isAdjacentTo(region) && !existing.overlaps(region) && existing.isSamePlaneAs(region)) {
                    merged.set(i, existing.merge(region));
                    wasMerged = true;
                    break;
                }
            }
            if (!wasMerged) {
                merged.add(region);
            }
        }
        this.regions.clear();
        this.regions.addAll(merged);
    }

    // --- Getters ---
    public UUID getId() { return id; }
    public String getName() { return name; }
    public UUID getOwner() { return owner; }
    public String getWorldName() { return worldName; }
    public List<CuboidRegion> getRegions() { return regions; }
    public long getCreatedAt() { return createdAt; }
    public int getRegionCount() { return regions.size(); }
}
