package org.almond.lands.model;

public enum LandPermission {
    BUILD("Place blocks", 0),
    BREAK("Break blocks", 0),
    INTERACT("Use doors/levers", 0),
    CONTAINER("Access chests", 0),
    MANAGE_MEMBERS("Add/remove members", 10),   // admin perm
    MANAGE_ROLES("Edit roles", 20),             // admin perm
    CLAIM("Create regions", 30),                // admin perm
    UNCLAIM("Delete regions", 50);              // admin perm

    private final String description;
    private final int weight;

    // Enum constructors are implicitly private
    LandPermission(String description, int weight) {
        this.description = description;
        this.weight = weight;
    }

    public String getDescription() {
        return this.description;
    }

    public int getWeight() {
        return this.weight;
    }
    
    public boolean isAdmin() {
        return this.weight > 0;
    }
}