package org.almond.buildinglore;

import org.almond.buildinglore.command.BuildingLoreCommand;
import org.almond.buildinglore.listener.LoreChatListener;
import org.almond.buildinglore.listener.WandListener;
import org.almond.buildinglore.manager.LoreDocumentManager;
import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.almond.buildinglore.visual.SelectionVisualizer;
import org.bukkit.command.PluginCommand;
import org.bukkit.plugin.java.JavaPlugin;

public class BuildingLorePlugin extends JavaPlugin {

    private SelectionManager selectionManager;
    private SelectionStorageManager storageManager;
    private SelectionVisualizer visualizer;
    private LoreDocumentManager loreManager;

    @Override
    public void onEnable() {
        // Initialize managers
        selectionManager = new SelectionManager();
        storageManager = new SelectionStorageManager(this);
        visualizer = new SelectionVisualizer(this, selectionManager);
        loreManager = new LoreDocumentManager();

        // Register listeners
        getServer().getPluginManager().registerEvents(new WandListener(selectionManager, visualizer), this);
        getServer().getPluginManager().registerEvents(new LoreChatListener(loreManager, storageManager), this);

        // Register the /bl command
        BuildingLoreCommand cmdExecutor = new BuildingLoreCommand(this, selectionManager, storageManager, visualizer, loreManager);
        PluginCommand blCommand = getCommand("bl");
        if (blCommand != null) {
            blCommand.setExecutor(cmdExecutor);
            blCommand.setTabCompleter(cmdExecutor);
        }

        getLogger().info("BuildingLore enabled.");
    }

    @Override
    public void onDisable() {
        visualizer.shutdown();
        getLogger().info("BuildingLore disabled.");
    }

    public SelectionManager getSelectionManager() {
        return selectionManager;
    }

    public SelectionStorageManager getStorageManager() {
        return storageManager;
    }

    public SelectionVisualizer getVisualizer() {
        return visualizer;
    }

    public LoreDocumentManager getLoreManager() {
        return loreManager;
    } 
}
