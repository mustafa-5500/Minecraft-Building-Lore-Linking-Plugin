package org.almond.buildinglore.visual;

import org.almond.buildinglore.manager.SelectionManager;
import org.almond.buildinglore.model.CuboidRegion;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Draws particle outlines around a player's current wand selection.
 * Particles are shown along the 12 edges of the cuboid at a configurable spacing.
 */
public class SelectionVisualizer {

    private final JavaPlugin plugin;
    private final SelectionManager selectionManager;

    /** Players who have visualization enabled */
    private final Set<UUID> enabledPlayers = new HashSet<>();

    /** The repeating task handle, or null if not running */
    private BukkitTask task;

    /** Particle spacing in blocks along each edge */
    private static final double PARTICLE_SPACING = 0.5;

    /** Ticks between each particle refresh (10 ticks = 0.5 seconds) */
    private static final long REFRESH_INTERVAL = 10L;

    public SelectionVisualizer(JavaPlugin plugin, SelectionManager selectionManager) {
        this.plugin = plugin;
        this.selectionManager = selectionManager;
    }

    /** Toggle visualization for a player. Returns the new state (true = on). */
    public boolean toggle(UUID playerId) {
        if (enabledPlayers.contains(playerId)) {
            enabledPlayers.remove(playerId);
            stopIfNoViewers();
            return false;
        } else {
            enabledPlayers.add(playerId);
            startIfNeeded();
            return true;
        }
    }

    public boolean isEnabled(UUID playerId) {
        return enabledPlayers.contains(playerId);
    }

    public void disable(UUID playerId) {
        enabledPlayers.remove(playerId);
        stopIfNoViewers();
    }

    /** Start the repeating particle task if it is not already running */
    private void startIfNeeded() {
        if (task != null) return;
        task = Bukkit.getScheduler().runTaskTimer(plugin, this::renderAll, 0L, REFRESH_INTERVAL);
    }

    /** Stop the task if nobody has visualization enabled */
    private void stopIfNoViewers() {
        if (!enabledPlayers.isEmpty()) return;
        if (task != null) {
            task.cancel();
            task = null;
        }
    }

    /** Called by the task each tick cycle — draws particles for all enabled players */
    private void renderAll() {
        for (UUID playerId : Set.copyOf(enabledPlayers)) {
            Player player = Bukkit.getPlayer(playerId);
            if (player == null || !player.isOnline()) {
                enabledPlayers.remove(playerId);
                continue;
            }
            renderForPlayer(player);
        }
        stopIfNoViewers();
    }

    private void renderForPlayer(Player player) {
        UUID playerId = player.getUniqueId();

        // Draw the in-progress wand selection (corner1/corner2)
        CuboidRegion preview = selectionManager.peekRegion(playerId);
        if (preview != null) {
            World world = Bukkit.getWorld(preview.getWorldName());
            if (world != null && world.equals(player.getWorld())) {
                drawCuboidEdges(player, world, preview, Color.LIME);
            }
        } else {
            // If only one corner is set, show a single point
            Location c1 = selectionManager.getCorner1(playerId);
            Location c2 = selectionManager.getCorner2(playerId);
            if (c1 != null && c1.getWorld() != null && c1.getWorld().equals(player.getWorld())) {
                spawnParticle(player, c1.getBlockX() + 0.5, c1.getBlockY() + 0.5, c1.getBlockZ() + 0.5, c1.getWorld(), Color.AQUA);
            }
            if (c2 != null && c2.getWorld() != null && c2.getWorld().equals(player.getWorld())) {
                spawnParticle(player, c2.getBlockX() + 0.5, c2.getBlockY() + 0.5, c2.getBlockZ() + 0.5, c2.getWorld(), Color.AQUA);
            }
        }
    }

    /**
     * Draws particles along the 12 edges of a cuboid.
     */
    private void drawCuboidEdges(Player player, World world, CuboidRegion region, Color color) {
        double x1 = region.getMinX();
        double y1 = region.getMinY();
        double z1 = region.getMinZ();
        double x2 = region.getMaxX() + 1.0; // +1 because block coords are inclusive
        double y2 = region.getMaxY() + 1.0;
        double z2 = region.getMaxZ() + 1.0;

        // 4 edges along X
        drawLine(player, world, x1, y1, z1, x2, y1, z1, color);
        drawLine(player, world, x1, y2, z1, x2, y2, z1, color);
        drawLine(player, world, x1, y1, z2, x2, y1, z2, color);
        drawLine(player, world, x1, y2, z2, x2, y2, z2, color);

        // 4 edges along Y
        drawLine(player, world, x1, y1, z1, x1, y2, z1, color);
        drawLine(player, world, x2, y1, z1, x2, y2, z1, color);
        drawLine(player, world, x1, y1, z2, x1, y2, z2, color);
        drawLine(player, world, x2, y1, z2, x2, y2, z2, color);

        // 4 edges along Z
        drawLine(player, world, x1, y1, z1, x1, y1, z2, color);
        drawLine(player, world, x2, y1, z1, x2, y1, z2, color);
        drawLine(player, world, x1, y2, z1, x1, y2, z2, color);
        drawLine(player, world, x2, y2, z1, x2, y2, z2, color);
    }

    /** Draws a particle line between two points */
    private void drawLine(Player player, World world, double x1, double y1, double z1,
                          double x2, double y2, double z2, Color color) {
        double dx = x2 - x1;
        double dy = y2 - y1;
        double dz = z2 - z1;
        double length = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (length == 0) return;

        int steps = Math.max(1, (int) (length / PARTICLE_SPACING));
        double stepX = dx / steps;
        double stepY = dy / steps;
        double stepZ = dz / steps;

        for (int i = 0; i <= steps; i++) {
            double px = x1 + stepX * i;
            double py = y1 + stepY * i;
            double pz = z1 + stepZ * i;
            spawnParticle(player, px, py, pz, world, color);
        }
    }

    /** Spawn a dust particle only visible to the given player */
    private void spawnParticle(Player player, double x, double y, double z, World world, Color color) {
        Particle.DustOptions dust = new Particle.DustOptions(color, 0.7f);
        player.spawnParticle(Particle.DUST, new Location(world, x, y, z), 1, 0, 0, 0, 0, dust);
    }

    /** Cleanup on plugin disable */
    public void shutdown() {
        if (task != null) {
            task.cancel();
            task = null;
        }
        enabledPlayers.clear();
    }
}
