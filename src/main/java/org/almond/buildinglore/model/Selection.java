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

    /**
     * Add a region to this selection, handling overlaps.
     * Adapted from org.almond.lands.manager.LandManager.claimRegion:
     * - If an existing region fully contains the new one, the new region is skipped.
     * - Existing regions fully contained by the new one are removed.
     * - Partial overlaps are resolved by subtracting existing regions from the new one.
     * - After adding, adjacent same-plane regions are merged.
     */
    public void addRegion(CuboidRegion region) {
        // If any existing region already fully contains the new one, nothing to add
        for (CuboidRegion existing : regions) {
            if (existing.containsRegion(region)) {
                return;
            }
        }

        // Remove any existing regions fully contained by the new region
        regions.removeIf(existing -> region.containsRegion(existing));

        // Subtract existing regions from the new region to get only the non-overlapping parts
        // (same pattern as LandManager.claimRegion splitting newRegions via subtract)
        Set<CuboidRegion> toAdd = new HashSet<>();
        toAdd.add(region);
        for (CuboidRegion existing : regions) {
            Set<CuboidRegion> nextToAdd = new HashSet<>();
            for (CuboidRegion piece : toAdd) {
                if (existing.overlaps(piece)) {
                    nextToAdd.addAll(piece.subtract(existing));
                } else {
                    nextToAdd.add(piece);
                }
            }
            toAdd = nextToAdd;
        }

        regions.addAll(toAdd);
        mergeRegions();
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

    /** Merge adjacent, same-plane regions to optimize the set.
     *  Adapted from org.almond.lands.model.Land.mergeRegions.
     *  Runs iteratively until no more merges are possible. */
    public void mergeRegions() {
        boolean changed = true;
        while (changed) {
            changed = false;
            List<CuboidRegion> merged = new ArrayList<>();
            for (CuboidRegion region : this.regions) {
                boolean wasMerged = false;
                for (int i = 0; i < merged.size(); i++) {
                    CuboidRegion existing = merged.get(i);
                    if (existing.isAdjacentTo(region) && !existing.overlaps(region) && existing.isSamePlaneAs(region)) {
                        merged.set(i, existing.merge(region));
                        wasMerged = true;
                        changed = true;
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
