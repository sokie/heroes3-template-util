"""Graphics scene managing zone and connection items."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGraphicsScene

from h3tc.editor.canvas.connection_item import ConnectionItem
from h3tc.editor.canvas.layout import (
    compute_zone_reids,
    force_directed_layout,
    image_settings_layout,
)
from h3tc.editor.canvas.zone_item import ZoneItem
from h3tc.models import Connection, TemplateMap, Zone


class TemplateScene(QGraphicsScene):
    """Scene that manages zone items and connection items for a template map."""

    zone_selected = Signal(object)  # Zone or None
    connection_selected = Signal(object)  # Connection or None
    selection_cleared = Signal()
    scene_modified = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._zone_items: dict[str, ZoneItem] = {}  # zone_id -> ZoneItem
        self._connection_items: list[ConnectionItem] = []
        self._template_map: TemplateMap | None = None
        self._snap_to_grid = False
        self.selectionChanged.connect(self._on_selection_changed)

    @property
    def snap_to_grid(self) -> bool:
        return self._snap_to_grid

    @snap_to_grid.setter
    def snap_to_grid(self, enabled: bool) -> None:
        self._snap_to_grid = enabled

    @property
    def template_map(self) -> TemplateMap | None:
        return self._template_map

    def load_map(
        self,
        template_map: TemplateMap,
        saved_positions: dict[str, tuple[float, float]] | None = None,
    ) -> None:
        """Load a template map onto the scene."""
        self.clear()
        self._zone_items.clear()
        self._connection_items.clear()
        self._template_map = template_map

        if not template_map.zones:
            return

        # Try image_settings positions first (HOTA editor coordinates)
        auto_positions = image_settings_layout(template_map)
        if auto_positions is None:
            # Fall back to grid-snapped force-directed layout
            auto_positions = force_directed_layout(template_map)
        positions = saved_positions or {}

        # Create zone items
        for zone in template_map.zones:
            zid = zone.id.strip()
            item = ZoneItem(zone)
            x, y = positions.get(zid, auto_positions.get(zid, (100, 100)))
            item.setPos(x, y)
            self.addItem(item)
            self._zone_items[zid] = item

        # Create connection items
        for conn in template_map.connections:
            z1 = conn.zone1.strip()
            z2 = conn.zone2.strip()
            if z1 in self._zone_items and z2 in self._zone_items:
                item = ConnectionItem(
                    conn, self._zone_items[z1], self._zone_items[z2]
                )
                self.addItem(item)
                self._connection_items.append(item)

    def zone_moved(self, zone_item: ZoneItem) -> None:
        """Called when a zone item is dragged. Updates connected lines."""
        zid = zone_item.zone.id.strip()
        for conn_item in self._connection_items:
            if (
                conn_item.zone1_item is zone_item
                or conn_item.zone2_item is zone_item
            ):
                conn_item.refresh_path()
        self.scene_modified.emit()

    def get_zone_positions(self) -> dict[str, tuple[float, float]]:
        """Get current zone positions for saving to sidecar."""
        positions = {}
        for zid, item in self._zone_items.items():
            pos = item.pos()
            positions[zid] = (pos.x(), pos.y())
        return positions

    def get_zone_item(self, zone_id: str) -> ZoneItem | None:
        return self._zone_items.get(zone_id)

    def add_zone(self, zone: Zone, x: float = 200, y: float = 200) -> ZoneItem:
        """Add a new zone to the scene and template map."""
        if self._template_map is None:
            return None
        self._template_map.zones.append(zone)
        item = ZoneItem(zone)
        item.setPos(x, y)
        self.addItem(item)
        self._zone_items[zone.id.strip()] = item
        self.scene_modified.emit()
        return item

    def add_connection(self, connection: Connection) -> ConnectionItem | None:
        """Add a new connection to the scene and template map."""
        if self._template_map is None:
            return None
        z1 = connection.zone1.strip()
        z2 = connection.zone2.strip()
        if z1 not in self._zone_items or z2 not in self._zone_items:
            return None

        self._template_map.connections.append(connection)
        item = ConnectionItem(
            connection, self._zone_items[z1], self._zone_items[z2]
        )
        self.addItem(item)
        self._connection_items.append(item)
        self.scene_modified.emit()
        return item

    def delete_selected(self) -> None:
        """Delete selected zones and connections."""
        if self._template_map is None:
            return

        for item in self.selectedItems():
            if isinstance(item, ZoneItem):
                zid = item.zone.id.strip()
                # Remove connections to this zone
                to_remove = [
                    ci
                    for ci in self._connection_items
                    if ci.zone1_item is item or ci.zone2_item is item
                ]
                for ci in to_remove:
                    self._template_map.connections.remove(ci.connection)
                    self._connection_items.remove(ci)
                    self.removeItem(ci)
                # Remove zone
                self._template_map.zones.remove(item.zone)
                del self._zone_items[zid]
                self.removeItem(item)

            elif isinstance(item, ConnectionItem):
                self._template_map.connections.remove(item.connection)
                self._connection_items.remove(item)
                self.removeItem(item)

        self.scene_modified.emit()

    def refresh_zone(self, zone: Zone) -> None:
        """Refresh a zone item's appearance after model changes."""
        zid = zone.id.strip()
        if zid in self._zone_items:
            self._zone_items[zid].refresh()

    def scale_zone_distances(self, factor: float) -> None:
        """Scale distances between all zones by factor (>1 = spread, <1 = compact)."""
        if not self._zone_items:
            return
        # Compute centroid
        cx, cy = 0.0, 0.0
        for item in self._zone_items.values():
            pos = item.pos()
            cx += pos.x()
            cy += pos.y()
        n = len(self._zone_items)
        cx /= n
        cy /= n
        # Scale positions relative to centroid
        for item in self._zone_items.values():
            pos = item.pos()
            nx = cx + (pos.x() - cx) * factor
            ny = cy + (pos.y() - cy) * factor
            item.setPos(nx, ny)
        # Refresh all connections
        for ci in self._connection_items:
            ci.refresh_path()
        self.scene_modified.emit()

    def refresh_connection(self, connection: Connection) -> None:
        """Refresh a connection item's appearance after model changes."""
        for ci in self._connection_items:
            if ci.connection is connection:
                ci.refresh_path()
                break

    def reid_zones(self, method: str = "dfs") -> dict[str, str] | None:
        """Re-ID all zones based on connectivity-preserving traversal.

        Args:
            method: "dfs" (depth-first) or "bfs" (breadth-first).

        Returns:
            Mapping of old_id -> new_id, or None if no changes needed.
        """
        if not self._template_map:
            return None

        positions = self.get_zone_positions()
        connections = [
            (c.zone1.strip(), c.zone2.strip())
            for c in self._template_map.connections
        ]
        mapping = compute_zone_reids(positions, connections, method=method)

        if not mapping:
            return None

        # Check if it's a no-op
        if all(old == new for old, new in mapping.items()):
            return None

        # Update zone IDs
        for zone in self._template_map.zones:
            old_id = zone.id.strip()
            if old_id in mapping:
                zone.id = mapping[old_id]

        # Update connection references
        for conn in self._template_map.connections:
            old1 = conn.zone1.strip()
            old2 = conn.zone2.strip()
            if old1 in mapping:
                conn.zone1 = mapping[old1]
            if old2 in mapping:
                conn.zone2 = mapping[old2]

        # Rebuild _zone_items dict with new keys (same ZoneItem objects)
        new_zone_items: dict[str, ZoneItem] = {}
        for old_id, item in self._zone_items.items():
            new_id = mapping.get(old_id, old_id)
            new_zone_items[new_id] = item
        self._zone_items = new_zone_items

        # Refresh all zone items to repaint ID labels
        for item in self._zone_items.values():
            item.refresh()

        self.scene_modified.emit()
        return mapping

    def _on_selection_changed(self) -> None:
        selected = self.selectedItems()
        if not selected:
            self.selection_cleared.emit()
            return
        item = selected[0]
        if isinstance(item, ZoneItem):
            self.zone_selected.emit(item.zone)
        elif isinstance(item, ConnectionItem):
            self.connection_selected.emit(item.connection)
