package org.almond.buildinglore.model;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * A named lore document attached to a Selection.
 * Contains ordered text entries that players can read.
 */
public class LoreDocument {
    private final UUID id;
    private final String name;
    private final List<String> entries;
    private final long createdAt;

    public LoreDocument(UUID id, String name, List<String> entries, long createdAt) {
        this.id = id;
        this.name = name;
        this.entries = new ArrayList<>(entries);
        this.createdAt = createdAt;
    }

    public LoreDocument(String name) {
        this(UUID.randomUUID(), name, new ArrayList<>(), System.currentTimeMillis());
    }

    public void addEntry(String text) {
        entries.add(text);
    }

    public boolean removeEntry(int index) {
        if (index < 0 || index >= entries.size()) return false;
        entries.remove(index);
        return true;
    }

    public String getFullText() {
        return String.join("\n", entries);
    }

    public UUID getId() { return id; }
    public String getName() { return name; }
    public List<String> getEntries() { return entries; }
    public long getCreatedAt() { return createdAt; }
    public int getEntryCount() { return entries.size(); }
}
