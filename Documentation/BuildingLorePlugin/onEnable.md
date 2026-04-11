# onEnable

## Signature
```java
@Override
public void onEnable()
```

## Description
Called by the server when the plugin is enabled. Initializes the `SelectionManager` and `SelectionStorageManager`, registers the `WandListener` for player interaction events, and binds the `BuildingLoreCommand` as executor and tab completer for the `/bl` command.

## Parameters
None.

## Returns
`void`
