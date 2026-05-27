package org.almond.buildinglore.manager;

import org.almond.buildinglore.model.LoreDocument;
import org.almond.buildinglore.model.Selection;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Manages the chat-based input flow for creating and editing lore documents.
 * Tracks per-player state: whether they are naming a new document or adding text to one.
 */
public class LoreDocumentManager {

    public enum InputMode {
        NAMING,   // Player is typing the name for a new lore document
        WRITING   // Player is typing lore text to append to a document
    }

    public static class InputState {
        private final InputMode mode;
        private final String selectionName;
        private final String documentName; // null when mode == NAMING

        public InputState(InputMode mode, String selectionName, String documentName) {
            this.mode = mode;
            this.selectionName = selectionName;
            this.documentName = documentName;
        }

        public InputMode getMode() { return mode; }
        public String getSelectionName() { return selectionName; }
        public String getDocumentName() { return documentName; }
    }

    private final Map<UUID, InputState> pendingInput = new HashMap<>();

    /** Start prompting a player to name a new lore document */
    public void startNaming(UUID player, String selectionName) {
        pendingInput.put(player, new InputState(InputMode.NAMING, selectionName, null));
    }

    /** Start prompting a player to write lore text */
    public void startWriting(UUID player, String selectionName, String documentName) {
        pendingInput.put(player, new InputState(InputMode.WRITING, selectionName, documentName));
    }

    /** Check if a player has pending lore input */
    public boolean hasPendingInput(UUID player) {
        return pendingInput.containsKey(player);
    }

    /** Get the current input state for a player */
    public InputState getInputState(UUID player) {
        return pendingInput.get(player);
    }

    /** Clear pending input for a player */
    public void clearInput(UUID player) {
        pendingInput.remove(player);
    }
}
