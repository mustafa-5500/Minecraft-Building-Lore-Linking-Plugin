# onCommand

## Signature
```java
@Override
public boolean onCommand(CommandSender sender, Command command, String label, String[] args)
```

## Description
Entry point for the `/bl` command. Ensures the sender is a player, then dispatches to the appropriate subcommand handler based on `args[0]`. Shows help if no arguments or unknown subcommand.

## Subcommands Dispatched
`wand`, `pos1`, `pos2`, `add`, `remove`, `list`, `info`, `delete`, `serialize`, `export`, `import`

## Returns
`boolean` — always `true` (command was handled).
