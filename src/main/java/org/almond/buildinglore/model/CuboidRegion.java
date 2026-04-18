package org.almond.buildinglore.model;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/**
 * A cuboid region defined by two corners (min and max block coordinates).
 * Adapted from org.almond.lands.model.Region for Paper/Bukkit.
 */
public class CuboidRegion {
    private final String worldName;
    private final int minX, minY, minZ;
    private final int maxX, maxY, maxZ;

    /** Constructor — corners are normalized to min/max automatically */
    public CuboidRegion(String worldName, int x1, int y1, int z1, int x2, int y2, int z2) {
        this.worldName = worldName;
        this.minX = Math.min(x1, x2);
        this.minY = Math.min(y1, y2);
        this.minZ = Math.min(z1, z2);
        this.maxX = Math.max(x1, x2);
        this.maxY = Math.max(y1, y2);
        this.maxZ = Math.max(z1, z2);
    }

    /** Checks if the given block position is within this region */
    public boolean contains(int x, int y, int z) {
        return x >= minX && x <= maxX &&
               y >= minY && y <= maxY &&
               z >= minZ && z <= maxZ;
    }

    /** Checks if this region overlaps with another region (same world only) */
    public boolean overlaps(CuboidRegion other) {
        if (!this.worldName.equals(other.worldName)) return false;
        return this.minX <= other.maxX && this.maxX >= other.minX &&
               this.minY <= other.maxY && this.maxY >= other.minY &&
               this.minZ <= other.maxZ && this.maxZ >= other.minZ;
    }

    /** Checks if this region fully contains another region */
    public boolean containsRegion(CuboidRegion other) {
        if (!this.worldName.equals(other.worldName)) return false;
        return this.minX <= other.minX && this.maxX >= other.maxX &&
               this.minY <= other.minY && this.maxY >= other.maxY &&
               this.minZ <= other.minZ && this.maxZ >= other.maxZ;
    }

    /** Checks if this region is adjacent (touching face-to-face) to another region */
    public boolean isAdjacentTo(CuboidRegion other) {
        if (!this.worldName.equals(other.worldName)) return false;

        boolean xAdj = (this.maxX + 1 == other.minX || this.minX - 1 == other.maxX) &&
                       (this.minY <= other.maxY && this.maxY >= other.minY) &&
                       (this.minZ <= other.maxZ && this.maxZ >= other.minZ);

        boolean yAdj = (this.maxY + 1 == other.minY || this.minY - 1 == other.maxY) &&
                       (this.minX <= other.maxX && this.maxX >= other.minX) &&
                       (this.minZ <= other.maxZ && this.maxZ >= other.minZ);

        boolean zAdj = (this.maxZ + 1 == other.minZ || this.minZ - 1 == other.maxZ) &&
                       (this.minX <= other.maxX && this.maxX >= other.minX) &&
                       (this.minY <= other.maxY && this.maxY >= other.minY);

        return xAdj || yAdj || zAdj;
    }

    /** Checks if two regions share the same plane along 2 axes (mergeable) */
    public boolean isSamePlaneAs(CuboidRegion other) {
        boolean xSame = this.minY == other.minY && this.maxY == other.maxY &&
                        this.minZ == other.minZ && this.maxZ == other.maxZ;

        boolean ySame = this.minX == other.minX && this.maxX == other.maxX &&
                        this.minZ == other.minZ && this.maxZ == other.maxZ;

        boolean zSame = this.minX == other.minX && this.maxX == other.maxX &&
                        this.minY == other.minY && this.maxY == other.maxY;

        return xSame || ySame || zSame;
    }

    /** Merge this region with another, producing the bounding box union */
    public CuboidRegion merge(CuboidRegion other) {
        return new CuboidRegion(
            this.worldName,
            Math.min(this.minX, other.minX), Math.min(this.minY, other.minY), Math.min(this.minZ, other.minZ),
            Math.max(this.maxX, other.maxX), Math.max(this.maxY, other.maxY), Math.max(this.maxZ, other.maxZ)
        );
    }

    /** Calculates the intersection with another region, or null if none */
    public CuboidRegion intersection(CuboidRegion other) {
        if (!this.overlaps(other)) return null;
        return new CuboidRegion(
            this.worldName,
            Math.max(this.minX, other.minX), Math.max(this.minY, other.minY), Math.max(this.minZ, other.minZ),
            Math.min(this.maxX, other.maxX), Math.min(this.maxY, other.maxY), Math.min(this.maxZ, other.maxZ)
        );
    }

    /** Subtracts another region from this one and returns the remaining pieces */
    public Set<CuboidRegion> subtract(CuboidRegion other) {
        if (!this.overlaps(other)) {
            return Set.of(this);
        }
        CuboidRegion inter = this.intersection(other);
        Set<CuboidRegion> remaining = new HashSet<>();

        // Left (negative X)
        if (this.minX < inter.minX) {
            remaining.add(new CuboidRegion(worldName, this.minX, this.minY, this.minZ, inter.minX - 1, this.maxY, this.maxZ));
        }
        // Right (positive X)
        if (this.maxX > inter.maxX) {
            remaining.add(new CuboidRegion(worldName, inter.maxX + 1, this.minY, this.minZ, this.maxX, this.maxY, this.maxZ));
        }
        // Bottom (negative Y) — constrained to intersection X range
        if (this.minY < inter.minY) {
            remaining.add(new CuboidRegion(worldName, inter.minX, this.minY, this.minZ, inter.maxX, inter.minY - 1, this.maxZ));
        }
        // Top (positive Y)
        if (this.maxY > inter.maxY) {
            remaining.add(new CuboidRegion(worldName, inter.minX, inter.maxY + 1, this.minZ, inter.maxX, this.maxY, this.maxZ));
        }
        // Front (negative Z) — constrained to intersection X and Y range
        if (this.minZ < inter.minZ) {
            remaining.add(new CuboidRegion(worldName, inter.minX, inter.minY, this.minZ, inter.maxX, inter.maxY, inter.minZ - 1));
        }
        // Back (positive Z)
        if (this.maxZ > inter.maxZ) {
            remaining.add(new CuboidRegion(worldName, inter.minX, inter.minY, inter.maxZ + 1, inter.maxX, inter.maxY, this.maxZ));
        }
        return remaining;
    }

    /** Block count of this cuboid */
    public long getVolume() {
        return (long)(maxX - minX + 1) * (maxY - minY + 1) * (maxZ - minZ + 1);
    }

    /** Compact string: (x1,y1,z1)-(x2,y2,z2) */
    @Override
    public String toString() {
        return "(" + minX + "," + minY + "," + minZ + ")-(" + maxX + "," + maxY + "," + maxZ + ")";
    }

    /** Parse from compact string produced by toString() */
    public static CuboidRegion fromString(String worldName, String s) {
        // Format: (x1,y1,z1)-(x2,y2,z2)
        String cleaned = s.replace("(", "").replace(")", "");
        String[] halves = cleaned.split("-", 2);
        String[] min = halves[0].split(",");
        String[] max = halves[1].split(",");
        return new CuboidRegion(
            worldName,
            Integer.parseInt(min[0].trim()), Integer.parseInt(min[1].trim()), Integer.parseInt(min[2].trim()),
            Integer.parseInt(max[0].trim()), Integer.parseInt(max[1].trim()), Integer.parseInt(max[2].trim())
        );
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        CuboidRegion other = (CuboidRegion) obj;
        return minX == other.minX && minY == other.minY && minZ == other.minZ &&
               maxX == other.maxX && maxY == other.maxY && maxZ == other.maxZ &&
               worldName.equals(other.worldName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(worldName, minX, minY, minZ, maxX, maxY, maxZ);
    }

    // --- Getters ---
    public String getWorldName() { return worldName; }
    public int getMinX() { return minX; }
    public int getMinY() { return minY; }
    public int getMinZ() { return minZ; }
    public int getMaxX() { return maxX; }
    public int getMaxY() { return maxY; }
    public int getMaxZ() { return maxZ; }
}
