from ezdxf.entities.polyline import DXFVertex, Polyline
from ezdxf.entities.spline import Spline
from ezdxf.entities.line import Line
from ezdxf.entities.insert import Insert
from ezdxf.entities.arc import Arc
from ezdxf.entities.dxfgfx import DXFGraphic
from ezdxf.math import BSpline, Vec3
from ezdxf import readfile, DXFStructureError
from shapely.geometry import Polygon, box
from apps.quoter.exceptions import DXFFileReadError, InvalidDXFFileError
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
import networkx as nx
from decimal import Decimal
import math

from apps.quoter.dxf import DXF2DGeometryHandler
import os


class DXF2DGeometryHandler1111:
    """
    A class to handle vector graphics from DXF files.

    This class reads a DXF file, processes its entities, and calculates the areas
    and perimeters of the figures represented by these entities. It is only capable
    of processing 2D figures.
    """

    def __init__(self, file_path: str) -> None:
        try:
            doc = readfile(filename=file_path)
        except IOError:
            raise DXFFileReadError(file_path)
        except DXFStructureError:
            raise InvalidDXFFileError(file_path)

        modelspace = doc.modelspace()
        print("len modelspace:", len(modelspace))
        self.COUNT = 0
        self._polygons: List[Polygon] = []
        self._lines: List[Tuple[Vec3]] = []
        self._groups_of_lines = []  # List to store groups of lines for each figure
        self._current_group = []  # List to store lines of the current figure

        for entity in modelspace:
            self._handle_entity(entity=entity)

        if self._current_group:
            self._groups_of_lines.append(self._current_group)

        self._areas = []
        self._perimeters = []

        for lines in self._groups_of_lines:
            print("group lines:", self._groups_of_lines)
            print("")
            print("lines:", lines)
            points = [(vertice[0].x, vertice[-1].y) for vertice in lines]
            print("")
            self._graphing_coordinates(points)
            print("points:", points)
            polygon = Polygon(points)
            self._areas.append(polygon.area)
            self._perimeters.append(polygon.length)
            self._polygons.append(polygon)

    @property
    def total_area(self) -> Decimal:
        """
        Return the total area of the figures.
        """

        total_area = sum(Decimal(area) for area in self._areas)
        containment_pairs = self._check_containment()

        for inner_index, outer_index in containment_pairs:
            total_area -= Decimal(self._areas[inner_index])

        return total_area

    @property
    def bounding_box_area(self) -> Decimal:
        """
        Calculate the area of the bounding box that contains all the figures.
        """

        if not self._polygons:
            return Decimal(0)

        min_x = min(polygon.bounds[0] for polygon in self._polygons)
        min_y = min(polygon.bounds[1] for polygon in self._polygons)
        max_x = max(polygon.bounds[2] for polygon in self._polygons)
        max_y = max(polygon.bounds[3] for polygon in self._polygons)

        bounding_box = box(min_x, min_y, max_x, max_y)

        return Decimal(bounding_box.area)

    @property
    def total_perimeter(self) -> Decimal:
        """
        Return the total perimeter of the figures.
        """

        return sum(Decimal(perimeter) for perimeter in self._perimeters)

    def _check_containment(self) -> List[Tuple[int, int]]:
        """
        Determines which polygons are contained within other polygons.

        This method iterates over all pairs of polygons stored in the instance and checks if one polygon is completely within another using the `within` method from the `shapely.geometry.Polygon` class. It returns a list of tuples where each tuple (inner_index, outer_index) indicates that the polygon at `inner_index` is inside the polygon at `outer_index`.

        #### Example:
            If there are three polygons:
            - Polygon 0: A large square
            - Polygon 1: A smaller circle inside the large square
            - Polygon 2: Another shape outside the large square

            The method would return `[(1, 0)]`, indicating that Polygon 1 is inside
            Polygon 0.
        """

        containment_pairs = []

        for i, outer_polygon in enumerate(self._polygons):
            for j, inner_polygon in enumerate(self._polygons):
                if i != j and inner_polygon.within(outer_polygon):
                    containment_pairs.append((j, i))

        return containment_pairs

    def _graphing_coordinates(self, coordinates: List[Tuple[float]]) -> None:
        x_values = [coord[0] for coord in coordinates]
        y_values = [coord[1] for coord in coordinates]
        x_values.append(coordinates[0][0])
        y_values.append(coordinates[0][1])
        # Plot the coordinates
        plt.plot(x_values, y_values, marker="o")

        # Set labels and title
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Graph of Coordinates")
        plt.axis("equal")

        # Display the plot
        plt.grid(True)
        plt.savefig("coordinates_plot.png")

    def _handle_entity(self, entity: DXFGraphic) -> None:
        """
        Handle a DXF entity and process it based on its type.
        """

        entity_type = entity.dxftype()
        print("type entity:", entity_type)
        if entity_type == "INSERT":
            self._handle_insert_entity(entity=entity)
        if entity_type == "POLYLINE":
            self._current_group.extend(self._handle_polyline_entity(entity=entity))
        if entity_type == "LINE":
            self._current_group.extend(self._handle_line_entity(entity=entity))
        if entity_type == "SPLINE":
            # If a SPLINE entity is detected, it represents a complete figure.
            # Therefore, we finalize the current group and start a new group for the SPLINE.
            if self._current_group:
                self._groups_of_lines.append(self._current_group)
                self._current_group = []

            self._current_group.extend(self._handle_spline_entity(entity=entity))
            self._groups_of_lines.append(self._current_group)
            self._current_group = []
        if entity_type == "ARC":
            arc_lines, start_point, end_point = self._handle_arc_entity(
                entity=entity
            )

            if self._current_group:
                last_point = self._current_group[-1][1]

                if self._is_close(last_point, start_point):
                    self._current_group.append((last_point, start_point))

            self._current_group.extend(arc_lines)

            if self._current_group:
                next_entity = self._get_next_entity(entity)

                if next_entity:
                    next_start_point = self._get_start_point(next_entity)

                    if self._is_close(end_point, next_start_point):
                        self._current_group.append((end_point, next_start_point))
        else:
            # For other entity types, finalize the current group
            if self._current_group:
                self._groups_of_lines.append(self._current_group)
                self._current_group = []

    def _handle_insert_entity(self, entity: Insert) -> None:
        """
        Handle an INSERT entity and process its block entities.
        """

        block = entity.block()

        for block_entity in block:
            self._handle_entity(entity=block_entity)

    def _handle_arc_entity(
        self, entity: Arc
    ) -> Tuple[List[Tuple[Vec3]], Vec3, Vec3]:
        """
        Handle an ARC entity and return a list of lines, start point, and end
        point.

        This method approximates the arc to get a smooth curve, removes duplicate
        points, and returns a list of lines represented as tuples of Vec3 points,
        along with the start and end points of the arc.
        """

        self._lines = []

        # Approximate the arc to get a smooth curve
        points = [Vec3(p) for p in entity.flattening(sagitta=0.01)]
        points = self._remove_duplicate_points(points=points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        start_point = points[0]
        end_point = points[-1]

        return self._lines, start_point, end_point

    def _handle_spline_entity(self, entity: Spline) -> List[Tuple[Vec3]]:
        """
        Handle a SPLINE entity and return a list of lines.

        This method approximates the spline to get a smooth curve, removes duplicate
        points, and returns a list of lines represented as tuples of Vec3 points.
        """

        self._lines = []

        # Approximate the spline to get a smooth curve
        bspline = BSpline(
            control_points=entity.control_points,
            order=entity.dxf.degree + 1,
            knots=entity.knots,
        )
        num_segments = self._calculate_segments(
            num_control_points=len(entity.control_points)
        )
        print(num_segments)
        points = [Vec3(p) for p in bspline.approximate(segments=num_segments)]
        print(num_segments)

        points = self._remove_duplicate_points(points=points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        return self._lines

    def _handle_polyline_entity(self, entity: Polyline) -> List[Tuple[Vec3]]:
        """
        Handle a POLYLINE entity and return a list of lines.

        This method processes the vertices of the polyline, removes duplicate lines,
        and returns a list of lines represented as tuples of Vec3 points.
        """

        self._lines = []
        vertices: List[DXFVertex] = entity.vertices

        for i in range(len(vertices) - 1):
            self._lines.append(
                (vertices[i].dxf.location, vertices[i + 1].dxf.location)
            )

        return self._remove_duplicate_lines(lines=self._lines)

    def _handle_line_entity(self, entity: Line) -> List[Tuple[Vec3]]:
        """
        Handle a LINE entity and return a list of lines.

        This method processes the start and end points of the line, removes
        duplicate lines, and returns a list of lines represented as tuples of Vec3
        points.
        """

        self._lines = []
        self._lines.append((entity.dxf.start, entity.dxf.end))

        return self._remove_duplicate_lines(lines=self._lines)

    @staticmethod
    def _calculate_segments(num_control_points: int) -> int:
        """
        Calculate the number of segments for approximating the spline based on the
        number of control points using a logarithmic scale.
        """

        return max(10, int(math.log2(num_control_points + 1) * 10))

    def _is_close(
        self, point1: Vec3, point2: Vec3, tolerance: float = 1e-6
    ) -> bool:
        """
        Check if two points are close enough to be considered connected.

        Args:
            point1: The first point.
            point2: The second point.
            tolerance: The distance tolerance to consider the points as connected.

        Returns:
            True if the points are close enough, False otherwise.
        """
        return point1.distance(point2) <= tolerance

    def _get_next_entity(self, current_entity: DXFGraphic) -> Optional[DXFGraphic]:
        """
        Get the next entity in the modelspace after the current entity.

        Args:
            current_entity: The current entity.

        Returns:
            The next entity if it exists, None otherwise.
        """
        modelspace = current_entity.doc.modelspace()
        entities = list(modelspace)
        current_index = entities.index(current_entity)
        if current_index < len(entities) - 1:
            return entities[current_index + 1]
        return None

    def _get_start_point(self, entity: DXFGraphic) -> Vec3:
        """
        Get the start point of an entity.

        Args:
            entity: The entity.

        Returns:
            The start point of the entity.
        """
        entity_type = entity.dxftype()
        if entity_type == "LINE":
            return entity.dxf.start
        elif entity_type == "ARC":
            return entity.start_point
        elif entity_type == "POLYLINE":
            return entity.vertices[0].dxf.location
        elif entity_type == "SPLINE":
            bspline = BSpline(
                control_points=entity.control_points,
                order=entity.dxf.degree + 1,
                knots=entity.knots,
            )
            points = [Vec3(p) for p in bspline.approximate(segments=10)]
            return points[0]
        return Vec3(0, 0, 0)

    @staticmethod
    def _remove_duplicate_points(points: List[Vec3]) -> List[Vec3]:
        """
        Remove consecutive duplicate points from the list.
        """

        filtered_points = [points[0]]

        for point in points[1:]:
            # Add point to the list if it is not the same as the last added point
            if point != filtered_points[-1]:
                filtered_points.append(point)

        return filtered_points

    @staticmethod
    def _remove_duplicate_lines(lines: List[Tuple[Vec3]]) -> List[Tuple[Vec3]]:
        """
        Remove duplicate lines from the list.
        """

        unique_lines = []

        for line in lines:
            if line not in unique_lines and (line[1], line[0]) not in unique_lines:
                unique_lines.append(line)

        return unique_lines


# Function to calculate the angle between two points
def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


# Function to traverse the graph in a clockwise direction
def traverse_clockwise(G, start_node):
    current_node = start_node
    visited_edges = set()
    path = [current_node]

    while True:
        neighbors = list(G.neighbors(current_node))
        if len(neighbors) == 0:
            break

        # Sort neighbors by angle in clockwise direction
        neighbors.sort(
            key=lambda x: calculate_angle(current_node, x), reverse=True
        )

        # Find the next edge that has not been visited
        next_node = None
        for neighbor in neighbors:
            if (current_node, neighbor) not in visited_edges and (
                neighbor,
                current_node,
            ) not in visited_edges:
                next_node = neighbor
                break

        if next_node is None:
            break

        # Mark the edge as visited
        visited_edges.add((current_node, next_node))
        visited_edges.add((next_node, current_node))

        # Move to the next node
        current_node = next_node
        path.append(current_node)

        # If we have returned to the start node, stop
        if current_node == start_node:
            break

    return path


def run():
    # cuadrado_chueco.dxf
    # cuadrado_chueco_c.dxf
    # cuadrado_dentro.dxf
    # cuadrado_dentro_c.dxf
    # cuadrado_100x100_pricut.dxf
    # 2 cuadrado.dxf
    # 2 cuadrado circulo.dxf
    # cuadrado_100x100_pricut_c.dxf
    # cuadrado.dxf
    # cuadrado_c.dxf
    # circulo_100_pricut.dxf
    # circulo_100_pricut_c.dxf
    # formaLoca.dxf
    # formas_1.dxf
    # forma_2_c.dxf
    # formas_juntas.dxf
    # cuadrado_(circulo)_200x200.dxf
    # circulo_(cuadrado)_200x200.dxf
    # formaLoca_(circulo)_250x200.dxf
    # formaLoca_(2circulos)_250x200.dxf
    # estrella5puntas_200x190,211.dxf
    # formaLoca_(2circulos)_250x200_agrupado.dxf
    # letraA_150x179,255.dxf
    # a.dxf
    # b contorno.dxf
    # B..contorno.dxf
    # messi.dxf
    # CHAPA BASE.step.DXF
    # lineas_+_cuandro.dxf
    # 8_bit_violin_laser_ready_3mm_soloCorte.dxf
    file_path = "/home/the-asintota/Escritorio/files/cuadrado_100x100_pricut.dxf"
    vector_graphic = DXF2DGeometryHandler(file_path=file_path)

    """for i, (area, perimeter) in enumerate(
        zip(vector_graphic._areas, vector_graphic._perimeters)
    ):
        print(f"Figure {i + 1} - Area: {area}, Perimeter: {perimeter}")

    print(f"Total Area: {vector_graphic.total_area}")
    print(f"Total Perimeter: {vector_graphic.total_perimeter}")
    print(vector_graphic.bounding_box_area)"""

    """graph = nx.Graph()
    lines = [
        ((10.0, 10.0), (0.0, 10.0)),
        ((10.0, 0.0), (0.0, 0.0)),
        ((10.0, 10.0), (10.0, 0.0)),
        ((0.0, 0.0), (0.0, 10.0)),
        ((20.0, 20.0), (30.0, 30.0)),
    ]
    # Add the lines to the graph
    for line in lines:
        vertex_start = line[0]
        vertex_end = line[1]
        graph.add_edge(vertex_start, vertex_end, line=line)

    # Find the connected components
    components = list(nx.connected_components(G=graph))

    # Extract edges for each connected component
    components_with_edges = []
    for component in components:
        subgraph = graph.subgraph(nodes=component)
        edges = list(subgraph.edges())
        components_with_edges.append((subgraph, edges))

    # print(components_with_edges)

    for subgraph, edges in components_with_edges:
        start_node = edges[0][0]
        path = traverse_clockwise(subgraph, start_node)
        print(path)"""


'''
class DXF2DGeometryHandler(DXFHandlerBase):
    """
    A class to handle vector graphics from DXF files.

    This class reads a DXF file, processes its entities, and calculates the areas
    and perimeters of the figures represented by these entities. It is only capable
    of processing 2D figures.
    """

    COMPLETE_FIGURE_ENTITIES = [Spline.DXFTYPE, Polyline.DXFTYPE, Circle.DXFTYPE]
    PRIMITIVE_ENTITIES = [Line.DXFTYPE, Arc.DXFTYPE, Insert.DXFTYPE]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        try:
            doc = readfile(filename=file_path)
        except IOError:
            raise DXFFileReadError(file_path=file_path)
        except DXFStructureError:
            raise InvalidDXFFileError(file_path=file_path)

        self._groups_lines: List[List[typing.Line]] = []
        self._groups_to_graphing: List[List[typing.Line]] = []
        self._polygons: List[Polygon] = []
        modelspace = doc.modelspace()

        print("num entities:", len(modelspace))
        for entity in modelspace:
            type_entity = entity.dxftype()
            print("type entity:", type_entity)

            if type_entity in self.COMPLETE_FIGURE_ENTITIES:
                handler = CompositeEntityHandler(entity=entity)

                if handler.is_closed:
                    self._polygons.append(handler.polygon)

                self._groups_lines.append(handler.lines)

                if "development" in CURRENT_SETTINGS:
                    self._groups_to_graphing.append(handler.lines)
                continue
            if type_entity in self.PRIMITIVE_ENTITIES:
                self._handle_entity(entity=entity)

        self._lines = self._remove_duplicate_lines(lines=self._lines)

        if self._lines:
            while True:
                if len(self._groups_lines) == 0:
                    self._groups_lines.append([self._lines[0]])
                    self._lines.pop(0)
                    continue

                group_index = 0

                while True:
                    print(1)
                    group = self._groups_lines[group_index]

                    while True:
                        print(2)
                        if len(self._lines) == 0:
                            break
                        if group[-1] == 1:
                            break

                        self._connect_lines_to_polygon(
                            group=group, lines=self._lines
                        )

                    if len(self._lines) == 0:
                        break

                    self._groups_lines.append([self._lines[0]])
                    self._lines.pop(0)
                    group_index += 1

                if len(self._lines) == 0:
                    break

        for group in self._groups_lines:
            points = [group[i][0] for i in range(len(group) - 1)]
            polygon = Polygon(points)
            self._polygons.append(polygon)

            if "development" in CURRENT_SETTINGS:
                self._groups_to_graphing.append(handler.lines)

        if "development" in CURRENT_SETTINGS:
            self._graphing_coordinates(groups_lines=self._groups_to_graphing)

        print("num polygons:", len(self._polygons))
        print("num groups:", len(self._groups_lines))
        # print("LINES:", self._lines)
        # print("GROUP:", self._groups_lines)

    def _handle_entity(self, entity: DXFGraphic) -> None:
        """
        Handle a DXF entity and process it based on its type.
        """

        map_entity_handler = {
            Line.DXFTYPE: self._handle_line_entity,
            Arc.DXFTYPE: self._handle_arc_entity,
            Insert.DXFTYPE: self._handle_insert_entity,
        }
        entity_type = entity.dxftype()

        try:
            map_entity_handler[entity_type](entity=entity)
        except KeyError as e:
            raise Exception(f"Error processing entity: {e}")

    def _handle_insert_entity(self, entity: Insert) -> None:
        """
        Handle an INSERT entity and process its block entities.
        """

        block = entity.block()
        print("num block entities:", len(block))
        for block_entity in block:
            type_entity = block_entity.dxftype()
            print("type block entity:", type_entity)

            if type_entity in self.COMPLETE_FIGURE_ENTITIES:
                handler = CompositeEntityHandler(entity=block_entity)
                self._polygons.append(handler.polygon)

                # Only test
                self._groups_to_graphing.append(handler.lines)
                continue
            if type_entity in self.PRIMITIVE_ENTITIES:
                self._handle_entity(entity=block_entity)

    def _handle_arc_entity(self, entity: Arc) -> None:
        """
        Handle an ARC entity and return a list of points.

        This method approximates the arc by generating points at regular intervals.
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

    def _build_polygons_from_lines(
        self, groups: List[List[typing.Line]], lines: List[typing.Line]
    ) -> None:
        """
        Processes the provided lines to construct polygons.

        This method takes a list of lines derived from the primitive entities and
        constructs one or more polygons that represent the design contained in the
        DXF file.
        """

        while True:
            if len(groups) == 0:
                groups.append([lines[0]])
                lines.pop(0)
                continue

            group_index = 0

            while True:
                group = groups[group_index]

                while True:
                    if len(lines) == 0:
                        break
                    if group[-1] == 1:
                        break

                    self._connect_lines_to_polygon(group=group, lines=lines)

                if len(lines) == 0:
                    break

                groups.append([lines[0]])
                lines.pop(0)
                group_index += 1

            if len(lines) == 0:
                break

    def _add_line_to_group(
        self, group: List[typing.Line], line: typing.Line
    ) -> bool:
        """
        Add the current line to the group if it is not a duplicate and is connected
        to either the first or the last line of the group. Also, check if the current
        line completes the polygon.
        """

        if len(group) >= 2:
            first_vertex = group[0][0]
            last_vertex = group[-1][1]

            # Check if the current line completes the polygon
            completes_polygon = (
                line[0] == first_vertex and line[1] == last_vertex
            ) or (line[1] == first_vertex and line[0] == last_vertex)

            if completes_polygon:
                self._connected(line=line, group=group)
                group.append(1)

                return True

        return self._connected(line=line, group=group)

    def _connect_lines_to_polygon(
        self, group: List[typing.Line], lines: List[typing.Line]
    ) -> None:
        """
        Connects lines that belong to a group.

        This method takes the lines obtained from the primitive entities and
        connects them with a group in the correct order to form a closed figure.
        """

        for i, line in enumerate(lines):
            if self._add_line_to_group(group=group, line=line):
                lines.pop(i)

                return None

    @staticmethod
    def _graphing_coordinates(groups_lines: List[List[typing.Line]]) -> None:

        for group in groups_lines:
            x_values = [group[i][0][0] for i in range(len(group) - 1)]
            y_values = [group[i][0][1] for i in range(len(group) - 1)]
            x_values.append(group[0][0][0])
            y_values.append(group[0][0][1])

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

    @staticmethod
    def _connected(line: typing.Line, group: List[Line]) -> bool:
        """
        Check if two lines are connected by comparing their endpoints.
        """

        first_line = group[0]
        last_line = group[-1]

        if len(group) == 1:
            if first_line[0] == line[0]:
                inverted_line = line[::-1]
                group.insert(0, inverted_line)

                return True
            if first_line[0] == line[1]:
                group.insert(0, line)

                return True
            if first_line[1] == line[0]:
                group.append(line)

                return True
            if first_line[1] == line[1]:
                inverted_line = line[::-1]
                group.append(inverted_line)

                return True

            return False
        if first_line[0] == line[0]:
            inverted_line = line[::-1]
            group.insert(0, inverted_line)

            return True
        if first_line[0] == line[1]:
            group.insert(0, line)

            return True
        if last_line[1] == line[0]:
            group.append(line)

            return True
        if last_line[1] == line[1]:
            inverted_line = line[::-1]
            group.append(inverted_line)

            return True

        return False

'''


'''
class DXF2DGeometryHandler22222222222222222:
    """
    A class to handle vector graphics from DXF files.

    This class reads a DXF file, processes its entities, and calculates the areas
    and perimeters of the figures represented by these entities. It is only capable
    of processing 2D figures.
    """

    def __init__(self, file_path: str) -> None:
        try:
            doc = readfile(filename=file_path)
        except IOError:
            raise DXFFileReadError(file_path=file_path)
        except DXFStructureError:
            raise InvalidDXFFileError(file_path=file_path)

        modelspace = doc.modelspace()
        self._polygons: List[Polygon] = []
        self._lines: List[Tuple[Vec3]] = []
        self._groups_of_lines = []  # List to store groups of lines for each figure
        self._current_group = []  # List to store lines of the current figure

        for entity in modelspace:
            self._handle_entity(entity=entity)

        if self._current_group:
            self._groups_of_lines.append(self._current_group)

        self._areas = []
        self._perimeters = []

        for lines in self._groups_of_lines:
            points = [(start.x, start.y) for start, _ in lines]
            polygon = Polygon(points)
            self._areas.append(polygon.area)
            self._perimeters.append(polygon.length)
            self._polygons.append(polygon)

    @property
    def total_area(self) -> Decimal:
        """
        Return the total area of the figures.
        """

        total_area = sum(Decimal(area) for area in self._areas)
        containment_pairs = self._check_containment()

        for inner_index, _ in containment_pairs:
            total_area -= Decimal(self._areas[inner_index])

        return total_area

    @property
    def total_perimeter(self) -> Decimal:
        """
        Return the total perimeter of the figures.
        """

        return sum(Decimal(perimeter) for perimeter in self._perimeters)

    @property
    def bounding_box_area(self) -> Decimal:
        """
        Calculate the area of the bounding box that contains all the figures.
        """

        if not self._polygons:
            return Decimal(0)

        min_x = min(polygon.bounds[0] for polygon in self._polygons)
        min_y = min(polygon.bounds[1] for polygon in self._polygons)
        max_x = max(polygon.bounds[2] for polygon in self._polygons)
        max_y = max(polygon.bounds[3] for polygon in self._polygons)

        bounding_box = box(min_x, min_y, max_x, max_y)

        return Decimal(bounding_box.area)

    def _check_containment(self) -> List[Tuple[int, int]]:
        """
        Determines which polygons are contained within other polygons.

        This method iterates over all pairs of polygons stored in the instance and checks if one polygon is completely within another using the `within` method from the `shapely.geometry.Polygon` class. It returns a list of tuples where each tuple (inner_index, outer_index) indicates that the polygon at `inner_index` is inside the polygon at `outer_index`.

        #### Example:
            If there are three polygons:
            - Polygon 0: A large square
            - Polygon 1: A smaller circle inside the large square
            - Polygon 2: Another shape outside the large square

            The method would return `[(1, 0)]`, indicating that Polygon 1 is inside
            Polygon 0.
        """

        containment_pairs = []

        for i, outer_polygon in enumerate(self._polygons):
            for j, inner_polygon in enumerate(self._polygons):
                if i != j and inner_polygon.within(outer_polygon):
                    containment_pairs.append((j, i))

        return containment_pairs

    def _handle_entity(self, entity: DXFGraphic) -> None:
        """
        Handle a DXF entity and process it based on its type.
        """

        entity_type = entity.dxftype()

        if entity_type == "INSERT":
            self._handle_insert_entity(entity=entity)
        if entity_type == "POLYLINE":
            self._current_group.extend(self._handle_polyline_entity(entity=entity))
        if entity_type == "LINE":
            self._current_group.extend(self._handle_line_entity(entity=entity))
        if entity_type == "SPLINE":
            # If a SPLINE entity is detected, it represents a complete figure.
            # Therefore, we finalize the current group and start a new group for the SPLINE.
            if self._current_group:
                self._groups_of_lines.append(self._current_group)
                self._current_group = []

            self._current_group.extend(self._handle_spline_entity(entity=entity))
            self._groups_of_lines.append(self._current_group)
            self._current_group = []
        if entity_type == "ARC":
            arc_lines, start_point, end_point = self._handle_arc_entity(
                entity=entity
            )

            if self._current_group:
                last_point = self._current_group[-1][1]

                if self._is_close(last_point, start_point):
                    self._current_group.append((last_point, start_point))

            self._current_group.extend(arc_lines)

            if self._current_group:
                next_entity = self._get_next_entity(entity)

                if next_entity:
                    next_start_point = self._get_start_point(next_entity)

                    if self._is_close(end_point, next_start_point):
                        self._current_group.append((end_point, next_start_point))
        else:
            # For other entity types, finalize the current group
            if self._current_group:
                self._groups_of_lines.append(self._current_group)
                self._current_group = []

    def _handle_insert_entity(self, entity: Insert) -> None:
        """
        Handle an INSERT entity and process its block entities.
        """

        block = entity.block()

        for block_entity in block:
            self._handle_entity(entity=block_entity)

    def _handle_arc_entity(
        self, entity: Arc
    ) -> Tuple[List[Tuple[Vec3]], Vec3, Vec3]:
        """
        Handle an ARC entity and return a list of lines, start point, and end
        point.

        This method approximates the arc to get a smooth curve, removes duplicate
        points, and returns a list of lines represented as tuples of Vec3 points,
        along with the start and end points of the arc.
        """

        self._lines = []

        # Approximate the arc to get a smooth curve
        points = [Vec3(p) for p in entity.flattening(sagitta=0.01)]
        points = self._remove_duplicate_points(points=points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        start_point = points[0]
        end_point = points[-1]

        return self._lines, start_point, end_point

    def _handle_spline_entity(self, entity: Spline) -> List[Tuple[Vec3]]:
        """
        Handle a SPLINE entity and return a list of lines.

        This method approximates the spline to get a smooth curve, removes duplicate
        points, and returns a list of lines represented as tuples of Vec3 points.
        """

        self._lines = []

        # Approximate the spline to get a smooth curve
        bspline = BSpline(
            control_points=entity.control_points,
            order=entity.dxf.degree + 1,
            knots=entity.knots,
        )
        num_segments = self._calculate_segments(
            num_control_points=len(entity.control_points)
        )
        points = [Vec3(p) for p in bspline.approximate(segments=num_segments)]
        points = self._remove_duplicate_points(points=points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        return self._lines

    def _handle_polyline_entity(self, entity: Polyline) -> List[Tuple[Vec3]]:
        """
        Handle a POLYLINE entity and return a list of lines.

        This method processes the vertices of the polyline, removes duplicate lines,
        and returns a list of lines represented as tuples of Vec3 points.
        """

        vertices: List[DXFVertex] = entity.vertices

        for i in range(len(vertices) - 1):
            self._lines.append(
                (vertices[i].dxf.location, vertices[i + 1].dxf.location)
            )

        return self._remove_duplicate_lines(lines=self._lines)

    def _handle_line_entity(self, entity: Line) -> List[Tuple[Vec3]]:
        """
        Handle a LINE entity and return a list of lines.

        This method processes the start and end points of the line, removes
        duplicate lines, and returns a list of lines represented as tuples of Vec3
        points.
        """

        self._lines.append((entity.dxf.start, entity.dxf.end))

        return self._remove_duplicate_lines(lines=self._lines)

    def _is_close(
        self, point1: Vec3, point2: Vec3, tolerance: float = 1e-6
    ) -> bool:
        """
        Check if two points are close enough to be considered connected.

        Args:
            point1: The first point.
            point2: The second point.
            tolerance: The distance tolerance to consider the points as connected.

        Returns:
            True if the points are close enough, False otherwise.
        """
        return point1.distance(point2) <= tolerance

    def _get_next_entity(self, current_entity: DXFGraphic) -> Optional[DXFGraphic]:
        """
        Get the next entity in the modelspace after the current entity.

        Args:
            current_entity: The current entity.

        Returns:
            The next entity if it exists, None otherwise.
        """
        modelspace = current_entity.doc.modelspace()
        entities = list(modelspace)
        current_index = entities.index(current_entity)
        if current_index < len(entities) - 1:
            return entities[current_index + 1]
        return None

    def _get_start_point(self, entity: DXFGraphic) -> Vec3:
        """
        Get the start point of an entity.

        Args:
            entity: The entity.

        Returns:
            The start point of the entity.
        """
        entity_type = entity.dxftype()
        if entity_type == "LINE":
            return entity.dxf.start
        elif entity_type == "ARC":
            return entity.start_point
        elif entity_type == "POLYLINE":
            return entity.vertices[0].dxf.location
        elif entity_type == "SPLINE":
            bspline = BSpline(
                control_points=entity.control_points,
                order=entity.dxf.degree + 1,
                knots=entity.knots,
            )
            points = [Vec3(p) for p in bspline.approximate(segments=10)]
            return points[0]
        return Vec3(0, 0, 0)

    @staticmethod
    def _calculate_segments(num_control_points: int) -> int:
        """
        Calculate the number of segments for approximating the spline based on the
        number of control points using a logarithmic scale.
        """

        return max(10, int(math.log2(num_control_points + 1) * 10))

    @staticmethod
    def _remove_duplicate_points(points: List[Vec3]) -> List[Vec3]:
        """
        Remove consecutive duplicate points from the list.
        """

        filtered_points = [points[0]]

        for point in points[1:]:
            # Add point to the list if it is not the same as the last added point
            if point != filtered_points[-1]:
                filtered_points.append(point)

        return filtered_points

    @staticmethod
    def _remove_duplicate_lines(lines: List[Tuple[Vec3]]) -> List[Tuple[Vec3]]:
        """
        Remove duplicate lines from the list.
        """

        unique_lines = []

        for line in lines:
            if line not in unique_lines and (line[1], line[0]) not in unique_lines:
                unique_lines.append(line)

        return unique_lines

////////////

class DXFHandlerBase:

    def __init__(self) -> None:
        self._lines: List[typing.Line] = []

    def _remove_duplicate_lines(
        self, lines: List[typing.Line]
    ) -> List[typing.Line]:
        """
        Remove duplicate and inverted lines from a list of lines.
        """

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
        """
        Normalize a line by ensuring the endpoints are in a consistent order.
        """

        if line[0] <= line[1]:
            return line
        else:
            return (line[1], line[0])

    @staticmethod
    def _remove_duplicate_points(
        points: List[typing.Vertex],
    ) -> List[typing.Vertex]:
        """
        Remove consecutive duplicate points from the list.
        """

        filtered_points = [points[0]]

        for point in points[1:]:
            # Add point to the list if it is not the same as the last added point
            if point != filtered_points[-1]:
                filtered_points.append(point)

        return filtered_points


class CompositeEntityHandler(DXFHandlerBase):
    """
    A class to handle composite entities.

    These entities represent complete figures by themselves. They are composed of
    multiple segments (lines or curves) that are connected together within a single
    entity.
    """

    def __init__(self, entity: DXFGraphic) -> None:
        super().__init__()
        self._polygon = None
        entity_type = entity.dxftype()
        map_entity_handler = {
            Spline.DXFTYPE: self._handle_spline_entity,
            Polyline.DXFTYPE: self._handle_polyline_entity,
            Circle.DXFTYPE: self._handle_circle_entity,
        }

        try:
            map_entity_handler[entity_type](entity=entity)
        except KeyError as e:
            raise Exception(f"Error processing entity: {e}")

    @property
    def polygon(self) -> Polygon:
        return self._polygon

    @property
    def lines(self) -> List[typing.Line]:
        return self._remove_duplicate_lines(lines=self._lines)

    def _handle_spline_entity(self, entity: Spline) -> None:
        """
        Handle a SPLINE entity and return a list of lines.

        This method approximates the spline to get a smooth curve, removes duplicate
        points, and returns a list of lines represented as tuples of Vec3 points.
        """

        bspline = BSpline(
            control_points=entity.control_points,
            order=entity.dxf.degree + 1,
            knots=entity.knots,
        )
        num_segments = self.calculate_segments(
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
        self._polygon = Polygon(points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        self._lines.append(1)

    def _handle_circle_entity(self, entity: Circle) -> None:
        """
        Handle a CIRCLE entity and return a list of points.

        This method approximates the circle by generating points at regular
        intervals.
        """

        angles = range(0, 360, 3)  # Generate points every 5 degrees
        points: List[typing.Vertex] = []

        for vertex in entity.vertices(angles):
            x = Decimal(vertex.x).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            y = Decimal(vertex.y).quantize(
                exp=Decimal("0.000"), rounding=ROUND_HALF_UP
            )
            points.append((x, y))

        points = self._remove_duplicate_points(points=points)
        self._polygon = Polygon(points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        self._lines.append(1)

    def _handle_polyline_entity(self, entity: Polyline) -> None:
        """
        Handle a POLYLINE entity and return a list of lines.

        This method processes the vertices of the polyline, removes duplicate lines,
        and returns a list of lines represented as tuples of Vec3 points.
        """

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
        self._polygon = Polygon(points)

        for i in range(len(points) - 1):
            self._lines.append((points[i], points[i + 1]))

        self._lines.append(1)

    @staticmethod
    def calculate_segments(num_control_points: int) -> int:
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

    COMPLETE_FIGURE_ENTITIES = [Spline.DXFTYPE, Polyline.DXFTYPE, Circle.DXFTYPE]
    PRIMITIVE_ENTITIES = [Line.DXFTYPE, Arc.DXFTYPE, Insert.DXFTYPE]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        try:
            doc = readfile(filename=file_path)
        except IOError:
            raise DXFFileReadError(file_path=file_path)
        except DXFStructureError:
            raise InvalidDXFFileError(file_path=file_path)

        self._groups_lines: List[List[typing.Line]] = []

        # Only test
        self._groups_to_graphing: List[List[typing.Line]] = []

        self._polygons: List[Polygon] = []
        modelspace = doc.modelspace()

        print("num entities:", len(modelspace))
        for entity in modelspace:
            entity_type = entity.dxftype()
            print("type entity:", entity_type)

            if entity_type in self.COMPLETE_FIGURE_ENTITIES:
                handler = CompositeEntityHandler(entity=entity)
                self._polygons.append(handler.polygon)

                # Only test
                self._groups_to_graphing.append(handler.lines)
                continue
            if entity_type in self.PRIMITIVE_ENTITIES:
                self._handle_entity(entity=entity)

        self._lines = self._remove_duplicate_lines(lines=self._lines)

        if self._lines:
            while True:
                if len(self._groups_lines) == 0:
                    self._groups_lines.append([self._lines[0]])
                    self._lines.pop(0)
                    continue

                group_index = 0

                while True:
                    group = self._groups_lines[group_index]

                    while True:
                        if len(self._lines) == 0:
                            break
                        if group[-1] == 1:
                            break

                        self._build_polygon(group=group, lines=self._lines)

                    if len(self._lines) == 0:
                        break

                    self._groups_lines.append([self._lines[0]])
                    self._lines.pop(0)
                    group_index += 1

                if len(self._lines) == 0:
                    break

        for group in self._groups_lines:
            points = [group[i][0] for i in range(len(group) - 1)]
            polygon = Polygon(points)
            self._polygons.append(polygon)

            # Only test
            self._groups_to_graphing.append(group)

        self._graphing_coordinates(groups_lines=self._groups_to_graphing)
        print("num polygons:", len(self._polygons))
        print("num groups:", len(self._groups_lines))
        # print("LINES:", self._lines)
        # print("GROUP:", self._groups_lines)

    def _handle_entity(self, entity: DXFGraphic) -> None:
        """
        Handle a DXF entity and process it based on its type.
        """

        map_entity_handler = {
            Line.DXFTYPE: self._handle_line_entity,
            Arc.DXFTYPE: self._handle_arc_entity,
            Insert.DXFTYPE: self._handle_insert_entity,
        }
        entity_type = entity.dxftype()

        try:
            map_entity_handler[entity_type](entity=entity)
        except KeyError as e:
            raise Exception(f"Error processing entity: {e}")

    def _handle_insert_entity(self, entity: Insert) -> None:
        """
        Handle an INSERT entity and process its block entities.
        """

        block = entity.block()
        print("num block entities:", len(block))
        for block_entity in block:
            entity_type = block_entity.dxftype()
            print("type block entity:", entity_type)

            if entity_type in self.COMPLETE_FIGURE_ENTITIES:
                handler = CompositeEntityHandler(entity=block_entity)
                self._polygons.append(handler.polygon)

                # Only test
                self._groups_to_graphing.append(handler.lines)
                continue
            if entity_type in self.PRIMITIVE_ENTITIES:
                self._handle_entity(entity=block_entity)

    def _handle_arc_entity(self, entity: Arc) -> None:
        """
        Handle an ARC entity and return a list of points.

        This method approximates the arc by generating points at regular intervals.
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

    def _add_line_to_group(
        self, group: List[typing.Line], line: typing.Line
    ) -> bool:
        """
        Add the current line to the group if it is not a duplicate and is connected
        to either the first or the last line of the group. Also, check if the current
        line completes the polygon.
        """

        if len(group) >= 2:
            first_vertex = group[0][0]
            last_vertex = group[-1][1]

            # Check if the current line completes the polygon
            completes_polygon = (
                line[0] == first_vertex and line[1] == last_vertex
            ) or (line[1] == first_vertex and line[0] == last_vertex)

            if completes_polygon:
                self._connected(line=line, group=group)
                group.append(1)

                return True

        return self._connected(line=line, group=group)

    def _build_polygon(
        self, group: List[typing.Line], lines: List[typing.Line]
    ) -> None:

        for i, line in enumerate(lines):
            if self._add_line_to_group(group=group, line=line):
                lines.pop(i)

                return None

    @staticmethod
    def _graphing_coordinates(groups_lines: List[List[typing.Line]]) -> None:

        for group in groups_lines:
            x_values = [group[i][0][0] for i in range(len(group) - 1)]
            y_values = [group[i][0][1] for i in range(len(group) - 1)]
            x_values.append(group[0][0][0])
            y_values.append(group[0][0][1])

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

    @staticmethod
    def _connected(line: typing.Line, group: List[Line]) -> bool:
        """
        Check if two lines are connected by comparing their endpoints.
        """

        first_line = group[0]
        last_line = group[-1]

        if len(group) == 1:
            if first_line[0] == line[0]:
                inverted_line = line[::-1]
                group.insert(0, inverted_line)

                return True
            if first_line[0] == line[1]:
                group.insert(0, line)

                return True
            if first_line[1] == line[0]:
                group.append(line)

                return True
            if first_line[1] == line[1]:
                inverted_line = line[::-1]
                group.append(inverted_line)

                return True

            return False
        if first_line[0] == line[0]:
            inverted_line = line[::-1]
            group.insert(0, inverted_line)

            return True
        if first_line[0] == line[1]:
            group.insert(0, line)

            return True
        if last_line[1] == line[0]:
            group.append(line)

            return True
        if last_line[1] == line[1]:
            inverted_line = line[::-1]
            group.append(inverted_line)

            return True

        return False

'''
