package org.almond.lands.manager;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.almond.lands.model.Land;
import org.almond.lands.model.Region;
import com.hypixel.hytale.math.vector.Vector3i;

public class SelectionManager {
    
    private Map<UUID, Vector3i> corner1 = new HashMap<>();
    private Map<UUID, Vector3i> corner2 = new HashMap<>();
    private Map<UUID, Boolean> selectionCompleted = new HashMap<>();

    public void setCorner1(UUID playerId, Vector3i position) {
        corner1.put(playerId, position);
    }

    public void setCorner2(UUID playerId, Vector3i position) {
        corner2.put(playerId, position);
    }

    public boolean isSelectionCompleted(UUID playerId) {
        return corner1.containsKey(playerId) && corner2.containsKey(playerId) && selectionCompleted.getOrDefault(playerId, false);
    }

    public Region getSelection(UUID playerId) {
        if (!isSelectionCompleted(playerId)) {
            return null;
        }
        return new Region(corner1.get(playerId), corner2.get(playerId));
    }

    public void completeSelection(UUID playerId) {
        if (corner1.containsKey(playerId) && corner2.containsKey(playerId)) {
            selectionCompleted.put(playerId, true);
        }
    }

    public void clearSelection(UUID playerId) {
        corner1.remove(playerId);
        corner2.remove(playerId);
        selectionCompleted.remove(playerId);
    }
}