# Selection (Constructors)

## Full Constructor
```java
public Selection(UUID id, String name, UUID owner, String worldName, List<CuboidRegion> regions, long createdAt)
```
Creates a selection with all fields specified. The regions list is defensively copied.

## Convenience Constructor
```java
public Selection(String name, UUID owner, String worldName)
```
Creates a new empty selection with an auto-generated UUID and current timestamp.

## Parameters (Full)
| Name | Type | Description |
|------|------|-------------|
| `id` | `UUID` | Unique identifier |
| `name` | `String` | Player-chosen display name |
| `owner` | `UUID` | UUID of the owning player |
| `worldName` | `String` | Minecraft world name |
| `regions` | `List<CuboidRegion>` | Initial regions |
| `createdAt` | `long` | Creation timestamp (epoch millis) |
