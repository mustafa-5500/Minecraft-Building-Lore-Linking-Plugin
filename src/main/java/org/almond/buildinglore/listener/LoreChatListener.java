package org.almond.buildinglore.listener;

import org.almond.buildinglore.manager.LoreDocumentManager;
import org.almond.buildinglore.manager.LoreDocumentManager.InputMode;
import org.almond.buildinglore.manager.LoreDocumentManager.InputState;
import org.almond.buildinglore.manager.SelectionStorageManager;
import org.almond.buildinglore.model.LoreDocument;
import org.almond.buildinglore.model.Selection;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;

import java.util.UUID;

/**
 * Listens for chat messages from players who are in lore input mode.
 * Captures their message as either a document name or lore text entry.
 */
public class LoreChatListener implements Listener {

    private static final String PREFIX = ChatColor.DARK_AQUA + "[BuildingLore] " + ChatColor.RESET;

    private final LoreDocumentManager loreManager;
    private final SelectionStorageManager storageManager;

    public LoreChatListener(LoreDocumentManager loreManager, SelectionStorageManager storageManager) {
        this.loreManager = loreManager;
        this.storageManager = storageManager;
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onChat(AsyncPlayerChatEvent event) {
        Player player = event.getPlayer();
        UUID playerId = player.getUniqueId();

        if (!loreManager.hasPendingInput(playerId)) {
            return;
        }

        event.setCancelled(true);
        String message = event.getMessage().trim();
        InputState state = loreManager.getInputState(playerId);

        // Allow cancellation
        if (message.equalsIgnoreCase("cancel")) {
            loreManager.clearInput(playerId);
            player.sendMessage(PREFIX + ChatColor.YELLOW + "Lore input cancelled.");
            return;
        }

        if (state.getMode() == InputMode.NAMING) {
            handleNaming(player, state, message);
        } else if (state.getMode() == InputMode.WRITING) {
            handleWriting(player, state, message);
        }
    }

    private void handleNaming(Player player, InputState state, String name) {
        UUID playerId = player.getUniqueId();
        Selection selection = storageManager.getSelection(playerId, state.getSelectionName());
        if (selection == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + state.getSelectionName() + "' no longer exists.");
            loreManager.clearInput(playerId);
            return;
        }

        if (selection.getLoreDocument(name) != null) {
            player.sendMessage(PREFIX + ChatColor.RED + "A lore document named '" + name + "' already exists in this selection. Try another name:");
            return;
        }

        LoreDocument doc = new LoreDocument(name);
        selection.addLoreDocument(doc);
        storageManager.saveSelection(selection);

        loreManager.clearInput(playerId);
        player.sendMessage(PREFIX + "Lore document " + ChatColor.GREEN + name + ChatColor.RESET +
                " created in selection " + ChatColor.GREEN + state.getSelectionName() + ChatColor.RESET + ".");
        player.sendMessage(PREFIX + "Use " + ChatColor.YELLOW + "/bl lore write " + state.getSelectionName() + " " + name +
                ChatColor.RESET + " to add text to it.");
    }

    private void handleWriting(Player player, InputState state, String text) {
        UUID playerId = player.getUniqueId();

        // "done" finishes writing mode
        if (text.equalsIgnoreCase("done")) {
            loreManager.clearInput(playerId);
            player.sendMessage(PREFIX + ChatColor.GREEN + "Finished writing to '" + state.getDocumentName() + "'.");
            return;
        }

        Selection selection = storageManager.getSelection(playerId, state.getSelectionName());
        if (selection == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Selection '" + state.getSelectionName() + "' no longer exists.");
            loreManager.clearInput(playerId);
            return;
        }

        LoreDocument doc = selection.getLoreDocument(state.getDocumentName());
        if (doc == null) {
            player.sendMessage(PREFIX + ChatColor.RED + "Lore document '" + state.getDocumentName() + "' no longer exists.");
            loreManager.clearInput(playerId);
            return;
        }

        doc.addEntry(text);
        storageManager.saveSelection(selection);
        player.sendMessage(PREFIX + ChatColor.GRAY + "Added line " + doc.getEntryCount() +
                ". Type more text, or type " + ChatColor.YELLOW + "done" + ChatColor.GRAY + " to finish.");
    }
}
