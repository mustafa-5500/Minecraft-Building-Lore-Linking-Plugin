package org.almond.buildinglore;

import org.almond.buildinglore.command.BuildingLoreCommand;
import org.almond.buildinglore.listener.WandListener;
import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.bukkit.command.PluginCommand;
import org.bukkit.plugin.java.JavaPlugin;

public class BuildingLorePlugin extends JavaPlugin {

    private SelectionManager selectionManager;
    private SelectionStorageManager storageManager;

    @Override
    public void onEnable() {
        // Initialize managers
        selectionManager = new SelectionManager();
        storageManager = new SelectionStorageManager(this);

        // Register the wand listener
        getServer().getPluginManager().registerEvents(new WandListener(selectionManager), this);

        // Register the /bl command
        BuildingLoreCommand cmdExecutor = new BuildingLoreCommand(this, selectionManager, storageManager);
        PluginCommand blCommand = getCommand("bl");
        if (blCommand != null) {
            blCommand.setExecutor(cmdExecutor);
            blCommand.setTabCompleter(cmdExecutor);
        }

        getLogger().info("BuildingLore enabled.");
    }

    @Override
    public void onDisable() {
        getLogger().info("BuildingLore disabled.");
    }

    public SelectionManager getSelectionManager() {
        return selectionManager;
    }

    public SelectionStorageManager getStorageManager() {
        return storageManager;
    }
}
