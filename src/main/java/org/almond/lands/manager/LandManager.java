package org.almond.lands.manager;

import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.UUID;
import java.util.Set;
import java.util.HashSet;
import java.lang.System;
import java.util.EnumSet;
import org.almond.lands.model.Land;
import org.almond.lands.model.Region;
import org.almond.lands.model.LandRole;
import org.almond.lands.model.LandPermission;
import com.hypixel.hytale.math.vector.Vector3i;

public class LandManager {

    private Map<UUID, Land> landsById = new HashMap<>();
    private Map<String, Land> landsByName = new HashMap<>();
    private Map<UUID, UUID> selectedLandByPlayer = new HashMap<>(); // Player UUID -> Selected Land UUID

    /** LandManager Constructor */
    public LandManager() {
        // Initialize with empty maps
        Map<UUID, Land> landsById = new HashMap<>();
        Map<String, Land> landsByName = new HashMap<>();
        Map<UUID, UUID> selectedLandByPlayer = new HashMap<>();
    }

    /** Creates a new land with default roles and adds it to the manager */
    public void createLand(String name, UUID ownerId, Region region) {
        UUID landId = UUID.randomUUID();
        Map<UUID, String> members = new HashMap<>();
        members.put(ownerId, "owner");
        Land land = new Land(landId, name, ownerId, Set.of(region), members, null, System.currentTimeMillis());
        landsById.put(landId, land);
        landsByName.put(name, land);
    }

    /** Deletes a land by its name */
    public void deleteLand(String name) {
        Land land = getLandByName(name);
        if (land != null) {
            // Only owner can delete the land
            if (!land.getOwner().equals(land.getMembers().keySet())) {
                throw new IllegalArgumentException("Only the land owner can delete the land.");
            }
            // TODO: Handle unselecting the land for players who have it selected (not implemented here for simplicity)
            // TODO: Handle notifying members of the land deletion (not implemented here for simplicity)
            // TODO: Go over what happens to members of the land (not implemented here for simplicity)
            landsById.remove(land.getId());
            landsByName.remove(name);
        } else {
            throw new IllegalArgumentException("Land with name " + name + " does not exist.");
        }
    }

    /** Selects a land for a player by land name */
    public void selectLandForPlayer(UUID playerId, String landName) {
        if (landsByName.containsKey(landName)) {
            UUID landId = landsByName.get(landName).getId();
            selectedLandByPlayer.put(playerId, landId);
        } else {
            throw new IllegalArgumentException("Land with name " + landName + " does not exist.");
        }
    }

    /** Clears the selected land for a player */
    public void clearSelectedLandForPlayer(UUID playerId) {
        selectedLandByPlayer.remove(playerId);
    }

    /** Retrieves the selected land for a player */
    public Land getSelectedLandForPlayer(UUID playerId) {
        UUID landId = selectedLandByPlayer.get(playerId);
        if (landId != null) {
            return landsById.get(landId);
        }
        return null;
    }

    /** Claims region for a land */
    public void claimRegion(UUID playerId, Region newRegion) {
        Land land = getSelectedLandForPlayer(playerId);
        if (land != null) {
            // Check permissions
            if (!checkPermission(playerId, land, LandPermission.CLAIM)) {
                throw new IllegalArgumentException("Player does not have permission to claim regions on this land.");
            }

            Boolean adjacent = false;
            Set<Region> newRegions = new HashSet<>();
            newRegions.add(newRegion);
            // Check for overlaps with existing regions
            for (Region newReg : newRegions) {
                for (Region region : land.getRegions()) {
                    if (region.isAdjacentTo(newReg)) {
                        adjacent = true;
                        newReg.addAdjacentRegion(region);
                    }
                    if (region.overlaps(newReg)) {
                        // overlapping also suggest adjacency
                        adjacent = true;
                        // Split the new region into non-overlapping parts
                        Set<Region> splitRegions = newReg.subtract(region);
                        newRegions.remove(newReg);
                        // The split Regions will not overlap with the existing regions.
                        // However, they are not guaranteed to be adjacent with each other.
                        // This is overlooked here, since the subtracted volume is represented by the new region.
                        // Therefore maintaining the adjacency.
                        newRegions.addAll(splitRegions);
                    }
                }
            }
            if(!adjacent) {
                throw new IllegalArgumentException("The new region must be adjacent to existing land regions.");
            }
            land.claimRegions(newRegions);
            land.mergeRegions();
            // Merge regions if necessary, to optimize storage and lookup (not implemented here for simplicity)
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Unclaims region for a land
     * Works on a copy of the regions to allow the player to cancel changes.
     * We need a deep copy of the region, since the subtract function effect the region adjacency set.
     */
    public void unclaimRegion(UUID playerId, Region regionToUnclaim) {
        Land land = getSelectedLandForPlayer(playerId);
        if (land != null) {

            // Check permissions
            if (!checkPermission(playerId, land, LandPermission.UNCLAIM)) {
                throw new IllegalArgumentException("Player does not have permission to unclaim regions on this land.");
            }

            Set<Region> landRegions = land.getRegionsCopy();
            Set<Region> regionsToRemove = new HashSet<>();
            Set<Region> regionsToAdd = new HashSet<>();
            for (Region region : land.getRegions()) {
                if (region.overlaps(regionToUnclaim)) {
                    // Subtract the unclaim region from the existing region
                    Set<Region> remainingRegions = region.subtract(regionToUnclaim);
                    region.clearAdjacentRegions();
                    regionsToRemove.add(region);
                    regionsToAdd.addAll(remainingRegions);
                }
            }
            landRegions.removeAll(regionsToRemove);
            landRegions.addAll(regionsToAdd);

            // Find the volume groups if they got Split
            Map<Set<Region>, Long> volumeGroups = new HashMap<>();
            for (Region region : landRegions) {
                // First iteration 
                if (volumeGroups.isEmpty()) {
                    volumeGroups.put(region.bfsRegionGraph(), 0L);
                } else {
                    for (Set<Region> group : volumeGroups.keySet()) {
                        if (group.contains(region)) {
                            // already in a group, skip
                            break;
                        } else {
                            // Not in any of the continuous groups
                            // Means a new volume group is formed
                            volumeGroups.put(region.bfsRegionGraph(), 0L);
                            break;
                        }
                    }
                }
            }

            // Calculate the volume for each group
            for (Set<Region> group : volumeGroups.keySet()) {
                Long groupVolume = 0L;
                for (Region region : group) {
                    groupVolume += region.getVolume();
                }
                volumeGroups.put(group, groupVolume);
            }

            

            // To maintain the continuous land property, set only one group of the split regions as the new land regions.
            // Here we just pick the largest volume group for simplicity.
            Set<Region> largestGroup = null;
            long maxVolume = 0;
            for (Map.Entry<Set<Region>, Long> entry : volumeGroups.entrySet()) {
                if (entry.getValue() > maxVolume) {
                    maxVolume = entry.getValue();
                    largestGroup = entry.getKey();
                }
            }
            if (largestGroup != null) {
                landRegions = largestGroup;
            }
            
            // TODO: Present volumeGroups to the player,
            // Player will confirm if they which to unclaim all the smaller volumeGroups
            // Future Edge Case: If Land claims have districts, and different districts are controlled by different players,
            // We need to make sure the unclaiming player cannot unclaim regions that belong to other players.
            // Future Edge Case: If Land has subclaims, the subclaims remain even if they are left partially or fully in the wild.
            
            // After Players confirm their choice.
            land.setRegions(landRegions);
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Trust Player
     *  Give players a member role to the land.
     */
    public void trustPlayer(UUID playerId, UUID targetPlayerId, String roleName) {
        Land land = getSelectedLandForPlayer(playerId);
        // Check if the player selected a land
        if (land != null) {

            // Cannot assign role if not a member
            if (land.getMembers().containsKey(targetPlayerId)) {
                throw new IllegalArgumentException("Player is already a member of the land.");
            }

            // Cannot assign role to the land owner
            if (land.getOwner().equals(targetPlayerId)) {
                throw new IllegalArgumentException("Cannot assign role to the land owner.");
            }

            // Check if the player has permission to manage members
            LandRole playerRole = land.getRoles().get(land.getMembers().get(playerId));
            if (playerRole == null || 
                !land.getOwner().equals(playerId) || 
                !playerRole.getPermissions().contains(LandPermission.MANAGE_MEMBERS)) {
                throw new IllegalArgumentException("Player does not have permission to manage members on this land.");
            }

            // Check if the role exists in the land
            if (!land.getRoles().containsKey(roleName)) {
                throw new IllegalArgumentException("Role " + roleName + " does not exist in the land.");
            }

            // Assign the role to the target player
            land.getMembers().put(targetPlayerId, roleName);
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Untrust Player
     *  Remove players from the land.
     */
    public void untrustPlayer(UUID playerId, UUID targetPlayerId) {
        Land land = getSelectedLandForPlayer(playerId);
        // Check if the player selected a land
        if (land != null) {

            // Cannot untrust if target player is not a member
            if (!land.getMembers().containsKey(targetPlayerId)) {
                throw new IllegalArgumentException("Player is not a member of the land.");
            }

            // Cannot untrust themselves, though players can leave lands
            if (playerId.equals(targetPlayerId)) {
                throw new IllegalArgumentException("Player cannot untrust themselves.");
            }

            // Cannot untrust if not a member
            if (!land.getMembers().containsKey(targetPlayerId)) {
                throw new IllegalArgumentException("Player is not a member of the land.");
            }

            // Cannot untrust the land owner
            if (land.getOwner().equals(targetPlayerId)) {
                throw new IllegalArgumentException("Cannot untrust the land owner.");
            }

            // Check if the player has permission to manage members
            LandRole playerRole = land.getRoles().get(land.getMembers().get(playerId));
            if (playerRole == null || 
                !land.getOwner().equals(playerId) || 
                !playerRole.getPermissions().contains(LandPermission.MANAGE_MEMBERS)) {
                throw new IllegalArgumentException("Player does not have permission to manage members on this land.");
            }

            // Remove the target player from members
            land.getMembers().remove(targetPlayerId);
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Create Role */
    public void createRole(UUID playerId, String roleName, Set<LandPermission> permissions) {
        Land land = getSelectedLandForPlayer(playerId);
        // Check if the player selected a land
        if (land != null) {

            // Check if player is a member of the land
            if (!land.getMembers().containsKey(playerId)) {
                throw new IllegalArgumentException("Player is not a member of the land.");
            }

            // Check if the role already exists in the land
            if (land.getRoles().containsKey(roleName)) {
                throw new IllegalArgumentException("Role " + roleName + " already exists in the land.");
            }

            // Check if the player has permission to manage roles
            LandRole playerRole = land.getRoles().get(land.getMembers().get(playerId));
            if (playerRole == null || 
                !land.getOwner().equals(playerId) || 
                !playerRole.getPermissions().contains(LandPermission.MANAGE_ROLES)) {
                throw new IllegalArgumentException("Player does not have permission to manage roles on this land.");
            }

            // Create and add the new role to the land
            LandRole newRole = new LandRole(roleName, permissions);
            land.addRole(roleName, newRole);
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Delete Role */
    public void deleteRole(UUID playerId, String roleName) {
        Land land = getSelectedLandForPlayer(playerId);
        // Check if the player selected a land
        if (land != null) {

            // Check if player is a member of the land
            if (!land.getMembers().containsKey(playerId)) {
                throw new IllegalArgumentException("Player is not a member of the land.");
            }

            // Check if the role exists in the land
            if (!land.getRoles().containsKey(roleName)) {
                throw new IllegalArgumentException("Role " + roleName + " does not exist in the land.");
            }

            // Check if the player has permission to manage roles
            LandRole playerRole = land.getRoles().get(land.getMembers().get(playerId));
            if (playerRole == null || 
                !land.getOwner().equals(playerId) || 
                !playerRole.getPermissions().contains(LandPermission.MANAGE_ROLES)) {
                throw new IllegalArgumentException("Player does not have permission to manage roles on this land.");
            }

            // Remove the role from the land
            land.removeRole(roleName);

            // Find a non-admin role to reassign members
            String defaultRoleName = null;
            for (LandRole role : land.getRoles().values()) {
                if (!role.isAdmin()) {
                    defaultRoleName = role.getName();
                    break;
                }
            }

            // If no non-admin role exists, create a default "member" role
            if (defaultRoleName == null) {
                defaultRoleName = "member";
                Set<LandPermission> memberPerms = EnumSet.of(
                    LandPermission.BUILD,
                    LandPermission.BREAK,
                    LandPermission.INTERACT,
                    LandPermission.CONTAINER
                );
                LandRole defaultRole = new LandRole(defaultRoleName, memberPerms);
                land.addRole(defaultRoleName, defaultRole);
            }

            // Reassign members with the deleted role to a default role (e.g., "member")
            for (Map.Entry<UUID, String> entry : land.getMembers().entrySet()) {
                if (entry.getValue().equals(roleName)) {
                    land.getMembers().put(entry.getKey(), defaultRoleName);
                }
            }
            
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Set Role Permissions */
    public void setRolePermissions(UUID playerId, String roleName, Set<LandPermission> newPermissions) {
        Land land = getSelectedLandForPlayer(playerId);
        // Check if the player selected a land
        if (land != null) {

            // Check if player is a member of the land
            if (!land.getMembers().containsKey(playerId)) {
                throw new IllegalArgumentException("Player is not a member of the land.");
            }

            // Check if the role exists in the land
            if (!land.getRoles().containsKey(roleName)) {
                throw new IllegalArgumentException("Role " + roleName + " does not exist in the land.");
            }

            // Check if the player has permission to manage roles
            LandRole playerRole = land.getRoles().get(land.getMembers().get(playerId));
            if (playerRole == null || 
                !land.getOwner().equals(playerId) || 
                !playerRole.getPermissions().contains(LandPermission.MANAGE_ROLES)) {
                throw new IllegalArgumentException("Player does not have permission to manage roles on this land.");
            }

            // Player cannot modify their own role, unless owner
            if (land.getMembers().get(playerId).equals(roleName) && 
                !land.getOwner().equals(playerId)) {
                throw new IllegalArgumentException("Player cannot modify their own role.");
            }

            // Player cannot modify roles with higher admin weights than their own role
            if (land.getRoles().get(roleName).getWeight() > playerRole.getWeight() && 
                !land.getOwner().equals(playerId)) {
                throw new IllegalArgumentException("Player cannot modify roles with more permissions.");
            }

            // Update the permissions for the role
            LandRole role = land.getRoles().get(roleName);
            role.setPermissions(newPermissions);
        } else {
            throw new IllegalArgumentException("No land selected for the player.");
        }
    }

    /** Check if a player has a specific permission for the given land */
    public boolean checkPermission(UUID playerId, Land land, LandPermission permission) {
        if (land.getOwner().equals(playerId)) {
            return true; // Owner has all permissions
        }
        String roleName = land.getMembers().get(playerId);
        if (roleName == null) {
            return false; // Not a member, no permissions
        }
        LandRole role = land.getRoles().get(roleName);
        if (role == null) {
            return false; // Role not found, no permissions
        }
        return role.getPermissions().contains(permission);
    }

    /** Get player role in a land */
    public String getPlayerRole(UUID playerId, Land land) {
        return land.getMembers().get(playerId);
    }

    /** Retrieves a land that contains the given position */
    public Land getLandAt(Vector3i position) {
        for (Land land : landsById.values()) {
            for (Region region : land.getRegions()) {
                if (region.contains(position)) {
                    return land;
                }
            }
        }
        return null;
    }

    /** Retrieves a land by its unique identifier */
    public Land getLandById(UUID landId) {
        return landsById.get(landId);
    }

    /** Retrieves a land by its name */
    public Land getLandByName(String name) {
        return landsByName.get(name);
    }

    /** Retrieves a land by its owner's UUID */
    public Land getLandByOwner(UUID ownerId) {
        for (Land land : landsById.values()) {
            if (land.getOwner().equals(ownerId)) {
                return land;
            }
        }
        return null;
    }

    /** Returns all lands managed by this LandManager */
    public Set<Land> getAllLands() {
        return new HashSet<>(landsById.values());
    }
    
}