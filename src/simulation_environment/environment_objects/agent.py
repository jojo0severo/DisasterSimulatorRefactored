# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Entity.java

from simulation_environment.exceptions.exceptions import *


class Agent:

    def __init__(self, agent_token, role, role_name, cdm_location, agent_info):
        """
        [Object that represents an instance of an agents 'controller',
        responsible for the manipulation of all its perceptions]

        :param agent_token: 'Manipulated' agent's id.
        :param role: The agent's main function over the simulation,
        which covers its skills and limitations.
        """
        self.token = agent_token
        self.last_action = None
        self.last_action_result = False
        self.location = cdm_location
        self.route = []
        self.physical_storage_vector = []
        self.virtual_storage_vector = []
        self.is_active = True
        self.social_assets = []
        self.role = role_name
        self.physical_storage = role.physical_capacity
        self.virtual_storage = role.virtual_capacity
        self.virtual_capacity = role.virtual_capacity
        self.physical_capacity = role.physical_capacity
        self.actual_battery = role.battery
        self.max_charge = role.battery
        self.speed = role.speed
        self.destination_distance = 0
        self.abilities = role.abilities
        self.agent_info = agent_info

    def discharge(self):
        if self.destination_distance:
            self.actual_battery = self.actual_battery - int(self.speed / 5) \
                if self.actual_battery - self.speed / 5 \
                else 0

    def check_battery(self):
        return self.actual_battery - int(self.speed / 5) if self.actual_battery - self.speed / 5 else 0

    def charge(self):

        self.actual_battery = self.max_charge

    def add_physical_item(self, item):

        size = item.size
        if size > self.physical_storage:
            raise FailedCapacity('The agent does not have enough physical storage.')

        self.physical_storage -= size
        self.physical_storage_vector.append(item)

    def add_virtual_item(self, item):

        size = item.size
        if size > self.virtual_storage:
            raise FailedCapacity('The agent does not have enough physical storage.')

        self.virtual_storage -= size
        self.virtual_storage_vector.append(item)

    def remove_physical_item(self, item, amount=1):
        if self.physical_storage == self.physical_capacity:
            raise FailedItemAmount('The agents has no victims or water samples to deliver.')

        found_item = False
        removed = []
        for stored_item in self.physical_storage_vector:
            if item == stored_item.type and amount:
                found_item = True
                removed.append(stored_item)
                amount -= 1

            elif not amount:
                break

        if not found_item:
            raise FailedUnknownItem('No physical item with this ID is stored.')

        for removed_item in removed:
            self.physical_storage_vector.remove(removed_item)
            self.physical_storage += removed_item.size

        return removed

    def remove_virtual_item(self, item, amount=1):
        if self.virtual_storage == self.virtual_capacity:
            raise FailedItemAmount('The agents has no photos to deliver.')

        found_item = False
        removed = []
        for stored_item in self.virtual_storage_vector:

            if item == stored_item.type and amount:
                found_item = True
                removed.append(stored_item)
                amount -= 1

            elif not amount:
                break

        if not found_item:
            raise FailedUnknownItem('No virtual item with this ID is stored.')

        for removed_item in removed:
            self.virtual_storage_vector.remove(removed_item)
            self.virtual_storage += removed_item.size

        return removed

    def json(self):
        copy = self.__dict__.copy()
        del copy['agent_info']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        copy['route'] = [{'lat': position[0], 'lon': position[1]} for position in copy['route']]
        return copy
