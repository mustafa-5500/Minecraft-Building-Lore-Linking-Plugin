# onTabComplete

## Signature
```java
@Override
public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args)
```

## Description
Provides tab completion suggestions. For the first argument, suggests all subcommand names. For the second argument on subcommands that take a selection name, suggests the player's existing selection names.

## Returns
`List<String>` — filtered suggestions matching the partial input.
