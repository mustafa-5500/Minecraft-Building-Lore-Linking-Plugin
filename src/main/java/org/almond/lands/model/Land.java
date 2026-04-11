package org.almond.lands.model;

import java.util.Map;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.UUID;
import org.almond.lands.model.Region;
import org.almond.lands.model.LandRole;
import org.almond.lands.model.LandPermission;
import com.hypixel.hytale.math.vector.Vector3i;

public class Land {
    private UUID id;                    // Unique land identifier
    private String name;                // Display name
    private UUID owner;                 // Owner's player UUID
    private Set<Region> regions;       // Claimed cuboid regions
    private Map<UUID, String> members;  // Player UUID -> Role name
    private Map<String, LandRole> roles; // Role name -> Role definition
    private long createdAt;             // Timestamp
    private long volume;                // Cached volume of the land

    /**
     * Returns a map of default roles for a land.
     * Roles: owner, admin, member, outsider
     */
    public static Map<String, LandRole> getDefaultRoles() {
        Map<String, LandRole> defaultRoles = new HashMap<>();

        // Owner: all permissions
        Set<LandPermission> ownerPerms = EnumSet.allOf(LandPermission.class);
        defaultRoles.put("owner", new LandRole("owner", ownerPerms));

        // Admin: all except MANAGE_ROLES, CLAIM, UNCLAIM
        Set<LandPermission> adminPerms = EnumSet.allOf(LandPermission.class);
        adminPerms.remove(LandPermission.MANAGE_ROLES);
        adminPerms.remove(LandPermission.CLAIM);
        adminPerms.remove(LandPermission.UNCLAIM);
        defaultRoles.put("admin", new LandRole("admin", adminPerms));

        // Member: basic build/break/interact/container
        Set<LandPermission> memberPerms = EnumSet.of(
            LandPermission.BUILD,
            LandPermission.BREAK,
            LandPermission.INTERACT,
            LandPermission.CONTAINER
        );
        defaultRoles.put("member", new LandRole("member", memberPerms));

        // Outsider: no permissions
        defaultRoles.put("outsider", new LandRole("outsider", EnumSet.noneOf(LandPermission.class)));

        return defaultRoles;
    }

    /** Constructor to create a land with given parameters */
    public Land(UUID id, String name, UUID owner, Set<Region> regions, Map<UUID, String> members,
                Map<String, LandRole> roles, long createdAt) {
        this.id = id;
        this.name = name;
        this.owner = owner;
        this.regions = new HashSet<>(regions);
        this.members = members;
        // If roles is null, use default roles
        this.roles = (roles != null) ? roles : getDefaultRoles();
        this.createdAt = createdAt;
        this.volume = getVolume();
    }

    /** Claims new regions for the land */
    public void claimRegions(Set<Region> newRegions) {
        this.regions.addAll(newRegions);
        this.volume = getVolume();
    }

    /** Unclaims regions from the land */
    public void unclaimRegions(Set<Region> regionsToUnclaim) {
        this.regions.removeAll(regionsToUnclaim);
        this.volume = getVolume();
    }

    /** Merges adjacent regions to optimize storage */
    public void mergeRegions() {
        Set<Region> merged = new HashSet<>();
        for (Region region : this.regions) {
            boolean mergedFlag = false;
            for (Region mRegion : merged) {
                if ((mRegion.isAdjacentTo(region)) && 
                    !(mRegion.overlaps(region)) && 
                    (mRegion.isSamePlaneAs(region))) {
                    Region newRegion = mRegion.merge(region);
                    merged.remove(mRegion);
                    merged.add(newRegion);
                    mergedFlag = true;
                    break;
                }
            }
            // If not merged, add to merged list
            if (!mergedFlag) {
                merged.add(region);
            }
        }
        // Reset regions to merged list
        this.regions = merged;
    }

    /** Set Regions for the land 
     * Note: Use with caution as it replaces existing regions
    */
    public void setRegions(Set<Region> regions) {
        this.regions = regions;
    }

    /** Return Copy of Regions Set
     * This is a deep copy of the region set
     */
    public Set<Region> getRegionsCopy() {
        Set<Region> copy = new HashSet<>();
        for (Region region : this.regions) {
            if (!copy.contains(region)){
                Region copiedRegion = region.copy();
                copy.addAll(copiedRegion.bfsRegionGraph());
            }
        }
        return copy;
    }

    /** Add Role */
    public void addRole(String roleName, LandRole landRole) {
        // Redundant check since LandManager should handle this, but added for safety
        if (this.roles.containsKey(roleName)) {
            throw new IllegalArgumentException("Role " + roleName + " already exists in the land.");
        }
        this.roles.put(roleName, landRole);
    }

    /** Remove Role */
    public void removeRole(String roleName) {
        if (!this.roles.containsKey(roleName)) {
            throw new IllegalArgumentException("Role " + roleName + " does not exist in the land.");
        }
        this.roles.remove(roleName);
    }

    /** Get volume */
    public long getVolume() {
        long volume = 0;
        for (Region region : this.regions) {
            volume += region.getVolume();
        }
        return volume;
    }

    /** Getters for the fields */
    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public UUID getOwner() {
        return owner;
    }

    public Set<Region> getRegions() {
        return regions;
    }

    public Map<UUID, String> getMembers() {
        return members;
    }

    public Map<String, LandRole> getRoles() {
        return roles;
    }

    public long getCreatedAt() {
        return createdAt;
    }
}