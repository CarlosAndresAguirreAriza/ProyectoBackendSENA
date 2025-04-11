from apps.quoter.exceptions import InvalidDXFFileError, DXFEntityError
from apps.quoter import typing
from ezdxf.entities.lwpolyline import LWPolyline
from ezdxf.entities.polyline import Polyline
from ezdxf.entities.dxfgfx import DXFGraphic
from ezdxf.entities.circle import Circle
from ezdxf.entities.spline import Spline
from ezdxf.entities.insert import Insert
from ezdxf.entities.line import Line
from ezdxf.entities.arc import Arc
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import BSpline
from ezdxf import readfile, DXFStructureError
from shapely.geometry import Polygon
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Set, Tuple
import matplotlib.pyplot as plt
import networkx as nx
import math
import os


CURRENT_SETTINGS = os.getenv("DJANGO_SETTINGS_MODULE")


class DXFHandlerBase:
    """A base class to handle DXF entities."""

    def __init__(self) -> None:
        self._lines: List[typing.Line] = []

    def _remove_duplicate_lines(
        self, lines: List[typing.Line]
    ) -> List[typing.Line]:
        """Remove duplicate and inverted lines from a list of lines."""

        unique_lines = set()
        result = []

        for line in lines:
            if line == 1:
                result.append(1)

                return result

            normalized_line = self._normalize_line(line=line)

            if normalized_line not in unique_lines:
                unique_lines.add(normalized_line)
                result.append(line)

        return result

    @staticmethod
    def _normalize_line(line: typing.Line) -> typing.Line:
        """Normalize a line by ensuring the endpoints are in a consistent order."""

        if line[0] <= line[1]:
            return line
        else:
            return (line[1], line[0])

    @staticmethod
    def _remove_duplicate_points(
        points: List[typing.Vertex],
    ) -> List[typing.Vertex]:
        """Remove consecutive duplicate points from the list."""

        filtered_points = [points[0]]

        for point in points[1:]:
            # Add point to the list if it is not the same as the last added point
            if point != filtered_points[-1]:
                filtered_points.append(point)

        return filtered_points


class ComplexEntityHandler(DXFHandlerBase):
    """
    The ComplexEntityHandler class processes geometric entities that consist of
    multiple vertices or control points. These entities can form intricate shapes or
    paths in 2D or 3D space and can be open or closed.
    """

    def __init__(self, entity: DXFGraphic) -> None:
        super().__init__()
        self._polygon: Polygon = None
        self._points: List[typing.Vertex] = []
        self._is_closed = False
        type_entity = entity.dxftype()

        map_entity_handler = {
            Spline.DXFTYPE: self._handle_spline_entity,
            Polyline.DXFTYPE: self._handle_polyline_entity,
            Circle.DXFTYPE: self._handle_circle_entity,
            LWPolyline.DXFTYPE: self._handle_lwpolyline_entity,
        }

        try:
            map_entity_handler[type_entity](entity=entity)
        except KeyError as e:
            raise DXFEntityError(
                f"Error processing entity: {type_entity}. Invalid entity type."
            )

    @property
    def points(self) -> List[typing.Vertex]:
        """Returns the vertices that make up the processed entity."""

        return self._points

    @property
    def is_closed(self) -> bool:
        """
        `True` if the entity is closed. A closed entity has a connection from the
        last vertex of the lines that make up the entity to the first vertex.
        """

        return self._is_closed

    @property
    def polygon(self) -> Polygon | None:
        """
        Returns the polygon that represents the processed entity, provided that it
        is a closed figure.
        """

        return self._polygon

    @property
    def lines(self) -> List[typing.Line]:
        """
        Returns the lines that make up the processed entity, which can be a closed
        figure or a segment of a larger figure. If the figure is closed, the number
        `1` is added to the end of the list to indicate that it is a complete figure.
        """

        return self._remove_duplicate_lines(lines=self._lines)

    def _handle_spline_entity(self, entity: Spline) -> None:
        """
        Handles a SPLINE entity and obtains the lines that compose it.

        This method approximates the spline to obtain a smooth curve and eliminates
        duplicate points to obtains the lines represented as tuples of vertices.
        """

        bspline = BSpline(
            control_points=entity.control_points,
            order=entity.dxf.degree + 1,
            knots=entity.knots,
        )
        num_segments = self._calculate_segments(
            num_control_points=len(entity.control_points)
        )
        points: List[typing.Vertex] = []

        for vertex in bspline.approximate(segments=num_segments):
            x = Decimal(vertex.x).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            y = Decimal(vertex.y).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            points.append((x, y))

        points = self._remove_duplicate_points(points=points)

        if points[0] == points[-1]:
            self._polygon = Polygon(points)
            self._points = points
            self._is_closed = True
        else:
            for i in range(len(points) - 1):
                self._lines.append((points[i], points[i + 1]))

    def _handle_circle_entity(self, entity: Circle) -> None:
        """
        Handle a CIRCLE entity and obtain the lines that compose it.

        This method approximates the circle by generating points at regular
        intervals and eliminates duplicate points to obtain its lines represented as
        tuples of vertices.
        """

        angles = range(0, 360, 3)  # Generate points every 5 degrees
        points: List[typing.Vertex] = []

        for vertex in entity.vertices(angles=angles):
            x = Decimal(vertex.x).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            y = Decimal(vertex.y).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            points.append((x, y))

        points = self._remove_duplicate_points(points=points)
        self._polygon = Polygon(points)
        self._points = points
        self._is_closed = True

    def _handle_polyline_entity(self, entity: Polyline) -> None:
        """
        Handles a POLYLINE entity and obtains the lines that compose it.

        This method processes the vertices of the polyline and eliminates duplicate
        points to obtain its lines represented as tuples of vertices.

        #### Raises:
        - `DXFEntityError`: If the entity is not a 2D polyline.
        """

        if not entity.is_2d_polyline:
            type_entity = entity.dxftype()

            raise DXFEntityError(
                f"Invalid DXF entity: {type_entity}. Only 2D polylines are supported."
            )

        points: List[typing.Vertex] = []

        for vertex in entity.vertices:
            x = Decimal(vertex.dxf.location.x).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            y = Decimal(vertex.dxf.location.y).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            points.append((x, y))

        points = self._remove_duplicate_points(points=points)

        if points[0] == points[-1]:
            self._polygon = Polygon(points)
            self._points = points
            self._is_closed = True
        else:
            for i in range(len(points) - 1):
                self._lines.append((points[i], points[i + 1]))

    def _handle_lwpolyline_entity(self, entity: LWPolyline) -> None:
        """
        Handles a LWPOLYLINE entity and returns the lines.

        This method processes the vertices of the lwpolyline and removes duplicate
        points to obtain its lines represented as tuples of vertices.
        """

        points: List[typing.Vertex] = []

        for vertex in entity.vertices():
            x = Decimal(str(vertex[0])).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            y = Decimal(str(vertex[1])).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            points.append((x, y))

        points = self._remove_duplicate_points(points=points)

        if points[0] == points[-1]:
            self._polygon = Polygon(points)
            self._points = points
            self._is_closed = True
        else:
            for i in range(len(points) - 1):
                self._lines.append((points[i], points[i + 1]))

    @staticmethod
    def _calculate_segments(num_control_points: int) -> int:
        """
        Calculate the number of segments for approximating the spline based on the
        number of control points using a logarithmic scale.
        """

        return max(10, int(math.log2(num_control_points + 1) * 14))


class DXF2DGeometryHandler(DXFHandlerBase):
    """
    A class to handle vector graphics from DXF files.

    This class reads a DXF file, processes its entities, and calculates the areas
    and perimeters of the figures represented by these entities. It is only capable
    of processing 2D figures.
    """

    COMPLETE_FIGURE_ENTITIES = [
        Spline.DXFTYPE,
        Polyline.DXFTYPE,
        Circle.DXFTYPE,
        LWPolyline.DXFTYPE,
    ]
    PRIMITIVE_ENTITIES = [Line.DXFTYPE, Arc.DXFTYPE, Insert.DXFTYPE]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        try:
            doc = readfile(filename=file_path)
        except IOError:
            raise InvalidDXFFileError(message=f"Could not read file: {file_path}")
        except DXFStructureError as e:
            raise InvalidDXFFileError(message=e)

        self._groups_points: List[List[typing.Vertex]] = []
        self._groups_to_graphing: List[List[typing.Vertex]] = []
        self._polygons: List[Polygon] = []
        modelspace = doc.modelspace()
        self._read_layout(modelspace=modelspace)
        self._lines = self._remove_duplicate_lines(lines=self._lines)

        if self._lines:
            self._build_polygons_from_lines(lines=self._lines)

        for group in self._groups_points:
            if not len(group) >= 3:
                raise InvalidDXFFileError(
                    message="Design error. There are figures that are not closed."
                )

            polygon = Polygon(group)
            self._polygons.append(polygon)

            if "development" in CURRENT_SETTINGS:
                self._groups_to_graphing.append(group)

        if "development" in CURRENT_SETTINGS:
            self._graphing_coordinates(groups_points=self._groups_to_graphing)

    def _read_layout(self, modelspace: Modelspace) -> None:
        """
        Iterates through the entities in the DXF file and saves the lines that make
        up the vector design.
        """

        for entity in modelspace:
            type_entity = entity.dxftype()

            if type_entity in self.COMPLETE_FIGURE_ENTITIES:
                handler = ComplexEntityHandler(entity=entity)
                if handler.is_closed:
                    self._polygons.append(handler.polygon)

                    if "development" in CURRENT_SETTINGS:
                        self._groups_to_graphing.append(handler.points)
                else:
                    self._lines.extend(handler.lines)

                continue
            if type_entity in self.PRIMITIVE_ENTITIES:
                self._handle_entity(entity=entity)

    def _handle_entity(self, entity: DXFGraphic) -> None:
        """Handle a DXF entity and process it based on its type."""

        map_entity_handler = {
            Line.DXFTYPE: self._handle_line_entity,
            Arc.DXFTYPE: self._handle_arc_entity,
            Insert.DXFTYPE: self._handle_insert_entity,
        }
        type_entity = entity.dxftype()

        try:
            map_entity_handler[type_entity](entity=entity)
        except KeyError as e:
            raise DXFEntityError(
                f"Error processing entity: {type_entity}. Invalid entity type."
            )

    def _handle_insert_entity(self, entity: Insert) -> None:
        """Handle an INSERT entity and process its block entities."""

        block = entity.block()
        self._read_layout(modelspace=block)

    def _handle_arc_entity(self, entity: Arc) -> None:
        """
        Handle an ARC entity and saves the lines that make up the segment. This
        method approximates the arc by generating points at regular intervals.
        """

        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        difference = abs(int(start_angle) - int(end_angle))
        angles = entity.angles(num=difference // 5)
        points: List[typing.Vertex] = []

        for vertex in entity.vertices(angles=angles):
            x = Decimal(vertex.x).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            y = Decimal(vertex.y).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            points.append((x, y))

        points = self._remove_duplicate_points(points=points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

    def _handle_line_entity(self, entity: Line) -> None:
        """Handle a LINE entity and saves the lines that make up the segment."""

        start_x = Decimal(entity.dxf.start.x).quantize(
            exp=Decimal("0.000"), rounding=ROUND_HALF_UP
        )
        start_y = Decimal(entity.dxf.start.y).quantize(
            exp=Decimal("0.000"), rounding=ROUND_HALF_UP
        )
        end_x = Decimal(entity.dxf.end.x).quantize(
            exp=Decimal("0.000"), rounding=ROUND_HALF_UP
        )
        end_y = Decimal(entity.dxf.end.y).quantize(
            exp=Decimal("0.000"), rounding=ROUND_HALF_UP
        )
        current_line = ((start_x, start_y), (end_x, end_y))
        self._lines.append(current_line)

    def _build_polygons_from_lines(self, lines: List[typing.Line]) -> None:
        """Processes the provided lines to construct polygons."""

        # Create a graph
        graph = nx.Graph()

        # Add the lines to the graph
        for line in lines:
            vertex_start, vertex_end = line
            graph.add_edge(vertex_start, vertex_end)

        # Find the connected components
        components: List[Set[typing.Node]] = list(nx.connected_components(G=graph))

        # Extract edges for each connected component
        components_with_edges: List[Tuple[nx.Graph, typing.Edge]] = []

        for component in components:
            subgraph: nx.Graph = graph.subgraph(nodes=component)
            edges: List[typing.Edge] = list(subgraph.edges)
            components_with_edges.append((subgraph, edges))

        # Get the connected components sorted
        for subgraph, edges in components_with_edges:
            start_node = edges[0][0]
            path = self._get_path(graph=subgraph, start_node=start_node)
            self._groups_points.append(path)

    def _get_path(
        self, graph: nx.Graph, start_node: typing.Node
    ) -> List[typing.Node]:
        """
        This method orders the nodes of a graph starting from a start node. The
        ordered nodes will allow the polygon they form to be constructed.
        """

        current_node = start_node
        visited_edges = set()
        path = [current_node]

        while True:
            neighbors: List[typing.Node] = list(graph.neighbors(n=current_node))

            if len(neighbors) == 0:
                break

            # Sort the neighbor nodes
            neighbors.sort(
                key=lambda x: self._calculate_angle(current_node, x), reverse=True
            )

            # Find the next unvisited edge in the given order
            next_node = None

            for neighbor in neighbors:
                # fmt: off
                if (current_node, neighbor) not in visited_edges \
                and (neighbor, current_node) not in visited_edges:
                    next_node = neighbor
                    break
                # fmt: on
            if next_node is None:
                break

            # Mark the edge as visited
            visited_edges.add((current_node, next_node))
            visited_edges.add((next_node, current_node))

            # Move to the next node
            current_node = next_node
            path.append(current_node)

            if current_node == start_node:
                break

        return path

    @staticmethod
    def _calculate_angle(p1: typing.Node, p2: typing.Node) -> float:
        """
        Calculates the angle between two points p1 and p2.

        Use the atan2 function from the math module. The atan2 function returns the
        angle in radians between the positive x-axis and the `vector` of points. Th
        angle is measured counterclockwise from the positive x-axis.
        """

        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

    @staticmethod
    def _graphing_coordinates(groups_points: List[List[typing.Vertex]]) -> None:
        for group in groups_points:
            x_values = [vertex[0] for vertex in group]
            y_values = [vertex[1] for vertex in group]
            x_values.append(group[0][0])
            y_values.append(group[0][1])

            # Plot the coordinates
            plt.plot(x_values, y_values, marker=".")

        # Set labels and title
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Graph of Coordinates")
        plt.axis("equal")

        # Display the plot
        plt.grid(True)
        plt.savefig("coordinates_plot.png")
