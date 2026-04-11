package org.almond.buildinglore.serializer;

import org.almond.buildinglore.model.CuboidRegion;
import org.almond.buildinglore.model.Selection;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

/**
 * Reads actual block data from the world within a Selection's regions
 * and outputs structured text for model training.
 */
public class BlockDataExporter {

    /**
     * Export block data for a selection to a string.
     *
     * @param selection The Selection to export
     * @param world     The Bukkit World to read blocks from
     * @param skipAir   Whether to skip air blocks
     * @return The block data as structured text
     */
    public static String export(Selection selection, World world, boolean skipAir) {
        StringBuilder sb = new StringBuilder();
        sb.append("# Selection: ").append(selection.getName()).append('\n');
        sb.append("# World: ").append(selection.getWorldName()).append('\n');
        sb.append("# Regions: ").append(selection.getRegionCount()).append('\n');
        sb.append("# Total Volume: ").append(selection.getTotalVolume()).append('\n');
        sb.append("# Format: x,y,z | block_type | [block_state]\n");
        sb.append('\n');

        for (int idx = 0; idx < selection.getRegions().size(); idx++) {
            CuboidRegion region = selection.getRegions().get(idx);
            sb.append("## Region ").append(idx).append(": ").append(region.toString()).append('\n');

            for (int x = region.getMinX(); x <= region.getMaxX(); x++) {
                for (int y = region.getMinY(); y <= region.getMaxY(); y++) {
                    for (int z = region.getMinZ(); z <= region.getMaxZ(); z++) {
                        Block block = world.getBlockAt(x, y, z);
                        if (skipAir && block.getType().isAir()) continue;

                        BlockData data = block.getBlockData();
                        String type = block.getType().getKey().toString();
                        String stateStr = data.getAsString(true); // includes block states
                        // getAsString(true) returns e.g. "minecraft:oak_door[facing=east,open=true]"
                        // We want the part after the type, if any
                        String state = "";
                        int bracketIdx = stateStr.indexOf('[');
                        if (bracketIdx >= 0) {
                            state = stateStr.substring(bracketIdx);
                        }

                        sb.append(x).append(',').append(y).append(',').append(z);
                        sb.append(" | ").append(type);
                        if (!state.isEmpty()) {
                            sb.append(" | ").append(state);
                        }
                        sb.append('\n');
                    }
                }
            }
            sb.append('\n');
        }
        return sb.toString();
    }

    /**
     * Export block data for a selection directly to a file.
     *
     * @param selection The Selection to export
     * @param world     The Bukkit World
     * @param exportDir The directory to write to
     * @param skipAir   Whether to skip air blocks
     * @return The file that was written
     */
    public static File exportToFile(Selection selection, World world, File exportDir, boolean skipAir) throws IOException {
        if (!exportDir.exists()) {
            exportDir.mkdirs();
        }
        File file = new File(exportDir, selection.getName() + ".txt");
        try (PrintWriter writer = new PrintWriter(new FileWriter(file))) {
            writer.write(export(selection, world, skipAir));
        }
        return file;
    }
}
