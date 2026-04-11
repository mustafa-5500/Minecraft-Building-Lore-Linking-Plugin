# Getters

## Signatures
```java
public UUID getId()
public String getName()
public UUID getOwner()
public String getWorldName()
public List<CuboidRegion> getRegions()
public long getCreatedAt()
public int getRegionCount()
```

## Description
Accessors for the selection's fields. `getRegions()` returns the internal list (not a copy). `getRegionCount()` is a convenience for `getRegions().size()`.
