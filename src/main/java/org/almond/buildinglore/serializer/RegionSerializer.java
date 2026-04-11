package org.almond.buildinglore.serializer;

import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.Selection;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Converts a Selection to/from a compact text token for embedding in documents.
 *
 * Format: [BL:world_name|x1,y1,z1>x2,y2,z2|x3,y3,z3>x4,y4,z4]
 */
public class RegionSerializer {

    /** Serialize a Selection into a compact, copy-pasteable text token */
    public static String serialize(Selection selection) {
        StringBuilder sb = new StringBuilder();
        sb.append("[BL:").append(selection.getWorldName());
        for (CuboidRegion region : selection.getRegions()) {
            sb.append('|');
            sb.append(region.getMinX()).append(',').append(region.getMinY()).append(',').append(region.getMinZ());
            sb.append('>');
            sb.append(region.getMaxX()).append(',').append(region.getMaxY()).append(',').append(region.getMaxZ());
        }
        sb.append(']');
        return sb.toString();
    }

    /**
     * Parse a compact text token back into a Selection.
     * The owner UUID must be provided separately (not embedded in the token).
     */
    public static Selection deserialize(String token, UUID owner) {
        if (token == null || !token.startsWith("[BL:") || !token.endsWith("]")) {
            throw new IllegalArgumentException("Invalid BL token format");
        }
        // Strip [BL: and ]
        String inner = token.substring(4, token.length() - 1);
        String[] parts = inner.split("\\|");
        if (parts.length < 1) {
            throw new IllegalArgumentException("Invalid BL token: missing world name");
        }

        String worldName = parts[0];
        List<CuboidRegion> regions = new ArrayList<>();

        for (int i = 1; i < parts.length; i++) {
            String regionStr = parts[i];
            String[] corners = regionStr.split(">");
            if (corners.length != 2) {
                throw new IllegalArgumentException("Invalid region in BL token: " + regionStr);
            }
            String[] min = corners[0].split(",");
            String[] max = corners[1].split(",");
            if (min.length != 3 || max.length != 3) {
                throw new IllegalArgumentException("Invalid coordinates in BL token: " + regionStr);
            }
            regions.add(new CuboidRegion(
                worldName,
                Integer.parseInt(min[0].trim()), Integer.parseInt(min[1].trim()), Integer.parseInt(min[2].trim()),
                Integer.parseInt(max[0].trim()), Integer.parseInt(max[1].trim()), Integer.parseInt(max[2].trim())
            ));
        }

        return new Selection(UUID.randomUUID(), "imported", owner, worldName, regions, System.currentTimeMillis());
    }
}
