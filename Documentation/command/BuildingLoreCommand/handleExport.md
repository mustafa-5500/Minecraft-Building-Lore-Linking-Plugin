# handleExport

## Signature
```java
private void handleExport(Player player, String[] args)
```

## Description
Exports block data for a named selection to a text file at `plugins/BuildingLore/exports/<uuid>/<name>.txt`. Reads blocks synchronously from the world. Skips air blocks.

## Usage
`/bl export <name>`

## Requires
- `buildinglore.export` permission (op by default)
