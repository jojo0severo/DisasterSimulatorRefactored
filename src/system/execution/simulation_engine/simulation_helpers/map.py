import math
import pyroutelib3
import pathlib
from itertools import zip_longest


class Map:
    def __init__(self, map_location, proximity):
        map_location = str((pathlib.Path(__file__).parents[5] / map_location).absolute())
        self.router = pyroutelib3.Router("car", map_location)
        self.proximity = proximity/1000

    def restart(self, map_location, proximity):
        del self.router
        self.router = pyroutelib3.Router("car", map_location)
        self.proximity = proximity/1000

    def get_closest_node(self, lat, lon):
        return self.router.findNode(lat, lon)

    def get_node_coord(self, node):
        return self.router.nodeLatLon(node)

    def check_location(self, a, b):
        ax, ay = a
        bx, by = b

        if self.check_proximity(ax, bx):
            if self.check_proximity(ay, by):
                return True

        return False

    def check_proximity(self, a, b):
        if a >= b:
            if a - self.proximity <= b:
                return True

            return False

        if a + self.proximity >= b:
            return True
        return False

    def align_coords(self, lat, lon):
        return self.get_node_coord(self.get_closest_node(lat, lon))

    def get_route(self, start, end, role, speed, list_of_nodes):
        if role == 'drone':
            return self.generate_coordinates_for_drones(start, end, speed)

        elif role == 'boat':
            return self.generate_coordinates_for_boats(start, end, speed, list_of_nodes)

        else:
            if start not in list_of_nodes:
                result, nodes = self.router.doRoute(start, end)

                if result == 'no_route':
                    return False, [], 0

                checked_nodes = []
                for node in nodes:
                    if node in list_of_nodes:
                        return False, [], 0

                    checked_nodes.append(node)

                return True, checked_nodes, self.node_distance(start, end)

            return False, [], 0

    def nodes_in_radius(self, coord, radius):
        result = []
        for node in self.router.rnodes:
            if self.router.distance(self.node_to_radian(node), self.coords_to_radian(coord)) <= radius:
                result.append(node)
        return result

    def node_to_radian(self, node):
        return self.coords_to_radian(self.router.nodeLatLon(node))

    def coords_to_radian(self, coords):
        return list(map(math.radians, coords))

    def node_distance(self, node_x, node_y):
        return self.router.distance(self.node_to_radian(node_x), self.node_to_radian(node_y))

    def generate_coordinates_for_drones(self, start, end, speed):
        actual_x, actual_y = start

        if actual_x > end[0]:
            x_axis = self.decrease_until_reached(actual_x, end[0], speed) or [end[0]]
        else:
            x_axis = self.increase_until_reached(actual_x, end[0], speed) or [end[0]]

        if actual_y > end[1]:
            y_axis = self.decrease_until_reached(actual_y, end[1], speed) or [end[1]]
        else:
            y_axis = self.increase_until_reached(actual_y, end[1], speed) or [end[1]]

        longest = y_axis[-1] if len(x_axis) > len(y_axis) else x_axis[-1]
        distance = self.router.distance(self.coords_to_radian(start), self.coords_to_radian(end))

        return True, list(zip_longest(x_axis, y_axis, fillvalue=longest)), distance

    def generate_coordinates_for_boats(self, start, end, speed, list_of_nodes=None):
        start_node = self.get_closest_node(*start)
        end_node = self.get_closest_node(*end)

        if start_node in list_of_nodes:
            if end_node in list_of_nodes:
                actual_x, actual_y = start

                if actual_x > end[0]:
                    x_axis = self.decrease_until_reached(actual_x, end[0], speed, list_of_nodes) or [end[0]]
                else:
                    x_axis = self.increase_until_reached(actual_x, end[0], speed, list_of_nodes) or [end[0]]

                if actual_y > end[1]:
                    y_axis = self.decrease_until_reached(actual_y, end[1], speed, list_of_nodes) or [end[1]]
                else:
                    y_axis = self.increase_until_reached(actual_y, end[1], speed, list_of_nodes) or [end[1]]

                longest = y_axis[-1] if len(x_axis) > len(y_axis) else x_axis[-1]
                distance = self.router.distance(self.coords_to_radian(start), self.coords_to_radian(end))

                return True, list(zip_longest(x_axis, y_axis, fillvalue=longest)), distance
        return False, [], 0

    def decrease_until_reached(self, start, end, speed, list_of_nodes=None):
        if start == end:
            return [end]

        points = []
        while True:
            if start - .0005 * speed < end:
                points.append(end)
                break
            else:
                start -= .0005 * speed

            if list_of_nodes:
                node = self.get_closest_node(start, end)
                if node in list_of_nodes:
                    points.append(start)
                else:
                    return None
            else:
                points.append(start)

        return points

    def increase_until_reached(self, start, end, speed, list_of_nodes=None):
        if start == end:
            return [end]

        points = []
        while True:
            if start + .0005 * speed > end:
                points.append(end)
                break
            else:
                start += .0005 * speed

            if list_of_nodes:
                node = self.get_closest_node(start, end)
                if node in list_of_nodes:
                    points.append(start)
                else:
                    return None
            else:
                points.append(start)

        return points
