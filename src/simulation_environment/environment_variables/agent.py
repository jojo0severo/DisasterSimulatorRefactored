from simulation_environment.exceptions.exceptions import *


class Agent:

    def __init__(self, token, role_name, cdm_location, battery, speed, physical_capacity, virtual_capacity):
        self.is_active = True
        self.token = token
        self.role = role_name
        self.location = cdm_location
        self.max_charge = battery
        self.actual_battery = battery
        self.speed = speed
        self.virtual_storage = virtual_capacity
        self.virtual_capacity = virtual_capacity
        self.physical_storage = physical_capacity
        self.physical_capacity = physical_capacity
        self.physical_storage_vector = []
        self.virtual_storage_vector = []
        self.last_action = None
        self.last_action_result = False
        self.route = []
        self.social_assets = []
        self.destination_distance = 0

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
