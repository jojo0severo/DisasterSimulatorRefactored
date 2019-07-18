import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.cycle import Cycle

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
cycle = Cycle(config_json)


def test_connect_agent():
    assert cycle.connect_agent('token_agent')
    assert not cycle.connect_agent('token_agent')


def test_connect_asset():
    assert cycle.connect_social_asset('token_asset')
    assert not cycle.connect_social_asset('token_asset')


def test_disconnect_agent():
    assert cycle.disconnect_agent('token_agent')
    assert not cycle.disconnect_agent('token_agent')


def test_disconnect_asset():
    assert cycle.disconnect_social_asset('token_asset')
    assert not cycle.disconnect_social_asset('token_asset')


def test_get_agents_info():
    assert len(cycle.get_agents_info()) == 1

    cycle.connect_agent('token_agent1')

    assert len(cycle.get_agents_info()) == 2


def test_get_assets_info():
    assert len(cycle.get_assets_info()) == 1

    cycle.connect_social_asset('token_asset1')
    assert len(cycle.get_assets_info()) == 2


def test_get_step():
    assert cycle.get_step()


def test_activate_step():
    old = cycle.get_step()
    assert not old['flood'].active

    cycle.activate_step()
    new = cycle.get_step()

    assert new['flood'].active


def test_get_previous_steps():
    for i in range(1, 5):
        cycle.current_step = i
        cycle.activate_step()

    assert cycle.get_previous_steps()


def test_check_steps():
    assert not cycle.check_steps()
    cycle.current_step = 10
    assert cycle.check_steps()
    cycle.current_step = 4


def test_update_steps():
    old_period = cycle.steps[0]['flood'].period
    cycle.update_steps()
    new_period = cycle.steps[0]['flood'].period

    assert old_period != new_period


def test_nothing_just_setup_for_pytest():
    cycle.restart(config_json)
    for i in range(10):
        cycle.current_step = i
        cycle.activate_step()
        cycle.update_steps()


def test_check_abilities_and_resources():
    assert cycle._check_abilities_and_resources('token_agent', 'move')

    for i in range(1, 4):
        cycle.connect_agent(f'token{i + 1}_agent')

    cycle.connect_agent('agent_without_abilities')
    assert not cycle._check_abilities_and_resources('agent_without_abilities', 'move')

    cycle.connect_agent('agent_without_resources')
    assert not cycle._check_abilities_and_resources('agent_without_resources', 'charge')

    for i in range(1, 4):
        cycle.connect_social_asset(f'token{i + 1}_asset')

    cycle.connect_social_asset('asset_without_abilities')
    assert not cycle._check_abilities_and_resources('asset_without_abilities', 'move')

    cycle.connect_social_asset('asset_without_resources')
    assert not cycle._check_abilities_and_resources('asset_without_resources', 'charge')


def test_charge():
    loc = config_json['map']['centerLat'], config_json['map']['centerLon']
    cycle.agents_manager.edit_agent('token_agent1', 'location', loc)
    assert cycle._charge_agent('token_agent1', []) is None


def test_charge_failed_param():
    try:
        cycle._charge_agent('token_agent1', ['parameter_given'])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_charge_failed_location():
    cycle.agents_manager.edit_agent('token_agent1', 'location', [120, 120])
    try:
        cycle._charge_agent('token_agent1', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_move_agent():
    agent = cycle.agents_manager.get_agent('token3_agent')
    loc = list(agent.location)
    loc[0] = loc[0] + 5
    loc[1] = loc[1] + 5

    assert cycle._move_agent('token3_agent', loc) is None
    assert cycle.agents_manager.get_agent('token3_agent').route
    assert cycle.agents_manager.get_agent('token3_agent').destination_distance
    old_dist = [cycle.agents_manager.get_agent('token3_agent').destination_distance]

    cycle._move_agent('token3_agent', loc)
    cycle._move_agent('token3_agent', loc)

    loc = ['cdm']

    assert cycle._move_agent('token3_agent', loc) is None
    assert cycle.agents_manager.get_agent('token3_agent').route
    assert cycle.agents_manager.get_agent('token3_agent').destination_distance
    assert old_dist[0] != cycle.agents_manager.get_agent('token3_agent').destination_distance


def test_move_agent_failed_facility():
    try:
        cycle._move_agent('token3_agent', ['unknown_facility'])
        assert False
    except Exception as e:
        if str(e).endswith('Unknown facility.'):
            assert True
        else:
            assert False


def test_move_agent_failed_less_parameters():
    try:
        cycle._move_agent('token3_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_move_agent_failed_more_parameters():
    try:
        cycle._move_agent('token3_agent', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_move_agent_failed_battery():
    cycle.agents_manager.edit_agent('token3_agent', 'actual_battery', 0)
    try:
        cycle._move_agent('token3_agent', [10, 10])
        assert False
    except Exception as e:
        if str(e).endswith('Not enough battery to complete this step.'):
            assert True
        else:
            assert False


def test_move_agent_failed_unable():
    cycle.agents_manager.edit_agent('agent_without_abilities', 'abilities', ['move'])
    cycle.agents_manager.edit_agent('agent_without_abilities', 'location', [10, 10])
    loc = cycle.map.get_node_coord(cycle.steps[0]['flood'].list_of_nodes[3])
    try:
        cycle._move_agent('agent_without_abilities', loc)
        assert False
    except Exception as e:
        if str(e).endswith('Agent is not capable of entering flood locations.'):
            assert True
        else:
            assert False


def test_move_asset():
    asset = cycle.social_assets_manager.get_social_asset('token3_asset')
    loc = list(asset.location)
    loc[0] = loc[0] + 5
    loc[1] = loc[1] + 5

    assert cycle._move_asset('token3_asset', loc) is None
    assert cycle.social_assets_manager.get_social_asset('token3_asset').route
    assert cycle.social_assets_manager.get_social_asset('token3_asset').destination_distance
    old_dist = [cycle.social_assets_manager.get_social_asset('token3_asset').destination_distance]

    while cycle.social_assets_manager.get_social_asset('token3_asset').route[:-3]:
        cycle._move_asset('token3_asset', loc)

    loc = ['cdm']

    assert cycle._move_asset('token3_asset', loc) is None
    assert cycle.social_assets_manager.get_social_asset('token3_asset').route
    assert cycle.social_assets_manager.get_social_asset('token3_asset').destination_distance
    assert old_dist[0] != cycle.social_assets_manager.get_social_asset('token3_asset').destination_distance


def test_move_asset_failed_facility():
    try:
        cycle._move_asset('token3_asset', ['unknown_facility'])
        assert False
    except Exception as e:
        if str(e).endswith('Unknown facility.'):
            assert True
        else:
            assert False


def test_move_asset_failed_less_parameters():
    try:
        cycle._move_asset('token3_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_move_asset_failed_more_parameters():
    try:
        cycle._move_asset('token3_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_move_asset_failed_unable():
    cycle.social_assets_manager.edit_social_asset('asset_without_abilities', 'abilities', ['move'])
    cycle.social_assets_manager.edit_social_asset('asset_without_abilities', 'location', [10, 10])
    loc = cycle.map.get_node_coord(cycle.steps[0]['flood'].list_of_nodes[3])
    try:
        cycle._move_asset('asset_without_abilities', loc)
        assert False
    except Exception as e:
        if str(e).endswith('Asset is not capable of entering flood locations.'):
            assert True
        else:
            assert False


def test_rescue_victim_agent():
    victim_loc = cycle.steps[0]['victims'][0].location
    cycle.agents_manager.edit_agent('token4_agent', 'location', victim_loc)

    old_storage = [cycle.agents_manager.get_agent('token4_agent').physical_storage]
    assert cycle._rescue_victim_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get_agent('token4_agent')
    assert agent.physical_storage_vector
    assert agent.physical_storage != old_storage[0]


def test_rescue_victim_agent_failed_param():
    try:
        cycle._rescue_victim_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_rescue_victim_agent_failed_unknown():
    cycle.agents_manager.edit_agent('token4_agent', 'location', [10, 10])
    try:
        cycle._rescue_victim_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('No victim by the given location is known.'):
            assert True
        else:
            assert False


def test_rescue_victim_asset():
    victim_loc = cycle.steps[0]['victims'][0].location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', victim_loc)

    old_storage = [cycle.social_assets_manager.get_social_asset('token4_asset').physical_storage]
    assert cycle._rescue_victim_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')
    assert asset.physical_storage_vector
    assert asset.physical_storage != old_storage[0]


def test_rescue_victim_asset_failed_param():
    try:
        cycle._rescue_victim_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_rescue_victim_asset_failed_unknown():
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', [10, 10])
    try:
        cycle._rescue_victim_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('No victim by the given location is known.'):
            assert True
        else:
            assert False


def test_collect_water_agent():
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.agents_manager.edit_agent('token4_agent', 'location', loc)

    old_storage = [cycle.agents_manager.get_agent('token4_agent').physical_storage]
    assert cycle._collect_water_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get_agent('token4_agent')
    assert agent.physical_storage_vector
    assert agent.physical_storage != old_storage[0]


def test_collect_water_agent_failed_param():
    try:
        cycle._collect_water_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_collect_water_agent_failed_unknown():
    cycle.agents_manager.edit_agent('token4_agent', 'location', [10, 10])
    try:
        cycle._collect_water_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not in a location with a water sample event.'):
            assert True
        else:
            assert False


def test_collect_water_asset():
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', loc)

    old_storage = [cycle.social_assets_manager.get_social_asset('token4_asset').physical_storage]
    assert cycle._collect_water_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')
    assert asset.physical_storage_vector
    assert asset.physical_storage != old_storage[0]


def test_collect_water_asset_failed_param():
    try:
        cycle._collect_water_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_collect_water_asset_failed_unknown():
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', [10, 10])
    try:
        cycle._collect_water_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('The asset is not in a location with a water sample event.'):
            assert True
        else:
            assert False


def test_take_photo_agent():
    loc = cycle.steps[0]['photos'][0].location
    cycle.agents_manager.edit_agent('token4_agent', 'location', loc)

    old_storage = [cycle.agents_manager.get_agent('token4_agent').virtual_storage]
    assert cycle._take_photo_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get_agent('token4_agent')
    assert agent.virtual_storage_vector
    assert agent.virtual_storage != old_storage


def test_take_photo_agent_failed_param():
    try:
        cycle._take_photo_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_take_photo_agent_failed_unknown():
    cycle.agents_manager.edit_agent('token4_agent', 'location', [10, 10])
    try:
        cycle._take_photo_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not in a location with a photograph event.'):
            assert True
        else:
            assert False


def test_take_photo_asset():
    loc = cycle.steps[0]['photos'][0].location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', loc)

    old_storage = [cycle.social_assets_manager.get_social_asset('token4_asset').virtual_storage]
    assert cycle._take_photo_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')
    assert asset.virtual_storage_vector
    assert asset.virtual_storage != old_storage


def test_take_photo_asset_failed_param():
    try:
        cycle._take_photo_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_take_photo_asset_failed_unknown():
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', [10, 10])
    try:
        cycle._take_photo_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('The asset is not in a location with a photograph event.'):
            assert True
        else:
            assert False


def test_analyze_photo_agent():
    assert cycle._analyze_photo_agent('token4_agent', []) is None

    agent = cycle.agents_manager.get_agent('token4_agent')

    assert not agent.virtual_storage_vector
    assert agent.virtual_storage == agent.virtual_capacity


def test_analyze_photo_agent_failed_param():
    try:
        cycle._analyze_photo_agent('token4_agent', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_analyze_photo_agent_failed_no_photos():
    try:
        cycle._analyze_photo_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('The agent has no photos to analyze.'):
            assert True
        else:
            assert False


def test_analyze_photo_asset():
    assert cycle._analyze_photo_asset('token4_asset', []) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')

    assert not asset.virtual_storage_vector
    assert asset.virtual_storage == asset.virtual_capacity


def test_analyze_photo_asset_failed_param():
    try:
        cycle._analyze_photo_asset('token4_asset', [1])
        assert False
    except Exception as e:
        if str(e).endswith('Parameters were given.'):
            assert True
        else:
            assert False


def test_analyze_photo_asset_failed_no_photos():
    try:
        cycle._analyze_photo_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('The asset has no photos to analyze.'):
            assert True
        else:
            assert False


def test_search_social_asset_agent():
    assert cycle._search_social_asset_agent('token4_agent', ['doctor']) is None

    agent = cycle.agents_manager.get_agent('token4_agent')

    assert agent.social_assets


def test_search_social_asset_agent_failed_param():
    try:
        cycle._search_social_asset_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Wrong amount of parameters given.'):
            assert True
        else:
            assert False


def test_search_social_asset_agent_failed_purpose():
    try:
        cycle._search_social_asset_agent('token4_agent', ['unknown'])
        assert False
    except Exception as e:
        if str(e).endswith('No social asset found for the needed purposes.'):
            assert True
        else:
            assert False


def test_search_social_asset_agent_failed_no_assets():
    cycle.social_assets_manager.social_assets.clear()
    cycle.social_assets_manager.capacities = cycle.social_assets_manager.generate_objects(config_json['map'], config_json['socialAssets'])
    try:
        cycle._search_social_asset_agent('token4_agent', ['doctor'])
        assert False
    except Exception as e:
        if str(e).endswith('No social asset connected.'):
            assert True
        else:
            assert False

    for i in range(1, 4):
        cycle.connect_social_asset(f'token{i + 1}_asset')


def test_search_social_asset_asset():
    assert cycle._search_social_asset_asset('token4_asset', ['doctor']) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')

    assert asset.social_assets


def test_search_social_asset_asset_failed_param():
    try:
        cycle._search_social_asset_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Wrong amount of parameters given.'):
            assert True
        else:
            assert False


def test_search_social_asset_asset_failed_purpose():
    try:
        cycle._search_social_asset_asset('token4_asset', ['unknown'])
        assert False
    except Exception as e:
        if str(e).endswith('No social asset found for the needed purposes.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent():
    loc = cycle.cdm_location
    cycle.agents_manager.edit_agent('token4_agent', 'location', loc)
    assert cycle._deliver_physical_agent('token4_agent', ['victim']) is None
    assert cycle._deliver_physical_agent('token4_agent', ['water_sample']) is None

    agent = cycle.agents_manager.get_agent('token4_agent')

    assert not agent.physical_storage_vector
    assert agent.physical_storage == agent.physical_capacity


def test_deliver_physical_agent_failed_less_param():
    try:
        cycle._deliver_physical_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent_failed_more_param():
    try:
        cycle._deliver_physical_agent('token4_agent', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_physical_agent_failed_location():
    cycle.agents_manager.edit_agent('token4_agent', 'location', [10, 10])
    try:
        cycle._deliver_physical_agent('token4_agent', ['victim'])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_physical_asset():
    loc = cycle.steps[0]['water_samples'][0].location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', loc)
    cycle._collect_water_asset('token4_asset', [])

    loc = cycle.cdm_location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', loc)
    assert cycle._deliver_physical_asset('token4_asset', ['water_sample']) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')

    assert not asset.physical_storage_vector
    assert asset.physical_storage == asset.physical_capacity


def test_deliver_physical_asset_failed_less_param():
    try:
        cycle._deliver_physical_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_physical_asset_failed_more_param():
    try:
        cycle._deliver_physical_asset('token4_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_physical_asset_failed_location():
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', [10, 10])
    try:
        cycle._deliver_physical_asset('token4_asset', ['water_sample'])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent():
    loc = cycle.steps[0]['photos'][0].location
    cycle.agents_manager.edit_agent('token4_agent', 'location', loc)
    cycle._take_photo_agent('token4_agent', [])

    loc = cycle.cdm_location
    cycle.agents_manager.edit_agent('token4_agent', 'location', loc)
    assert cycle._deliver_virtual_agent('token4_agent', ['photo']) is None

    agent = cycle.agents_manager.get_agent('token4_agent')

    assert not agent.virtual_storage_vector
    assert agent.virtual_storage == agent.virtual_capacity


def test_deliver_virtual_agent_failed_less_param():
    try:
        cycle._deliver_virtual_agent('token4_agent', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent_failed_more_param():
    try:
        cycle._deliver_virtual_agent('token4_agent', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_agent_failed_location():
    cycle.agents_manager.edit_agent('token4_agent', 'location', [10, 10])
    try:
        cycle._deliver_virtual_agent('token4_agent', ['photo'])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset():
    loc = cycle.steps[0]['photos'][0].location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', loc)
    cycle._take_photo_asset('token4_asset', [])

    loc = cycle.cdm_location
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', loc)
    assert cycle._deliver_virtual_asset('token4_asset', ['photo']) is None

    asset = cycle.social_assets_manager.get_social_asset('token4_asset')

    assert not asset.virtual_storage_vector
    assert asset.virtual_storage == asset.virtual_capacity


def test_deliver_virtual_asset_failed_less_param():
    try:
        cycle._deliver_virtual_asset('token4_asset', [])
        assert False
    except Exception as e:
        if str(e).endswith('Less than 1 parameter was given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_failed_more_param():
    try:
        cycle._deliver_virtual_asset('token4_asset', [1, 2, 3])
        assert False
    except Exception as e:
        if str(e).endswith('More than 2 parameters were given.'):
            assert True
        else:
            assert False


def test_deliver_virtual_asset_failed_location():
    cycle.social_assets_manager.edit_social_asset('token4_asset', 'location', [10, 10])
    try:
        cycle._deliver_virtual_asset('token4_asset', ['photo'])
        assert False
    except Exception as e:
        if str(e).endswith('The agent is not located at the CDM.'):
            assert True
        else:
            assert False


def test_update_photos_state():
    identifiers = [photo.identifier for photo in cycle.steps[0]['photos']]
    cycle._update_photos_state(identifiers)

    for photo in cycle.steps[0]['photos']:
        assert photo.analyzed
        for victim in photo.victims:
            assert victim.active


def test_carry():
    special_action_tokens = [('token4_agent', 'carry', ['token4_asset']), ('token4_asset', 'getCarried', ['token4_agent'])]
    assert cycle._carry(0, special_action_tokens) == ('token4_agent', 'token4_asset')

    agent = cycle.agents_manager.get_agent('token4_agent')
    asset = cycle.social_assets_manager.get_social_asset('token4_asset')

    assert agent.last_action == 'carry'
    assert asset.last_action == 'getCarried'
    assert asset.carried

    special_action_tokens = [('token4_agent', 'carry', ['token4_asset']), ('token4_asset', 'getCarried', [''])]
    assert cycle._carry(0, special_action_tokens) == ('token4_agent', None)
    assert not agent.last_action_result


def test_get_carried():
    special_action_tokens = [('token4_agent', 'getCarried', ['token4_asset']), ('token4_asset', 'carry', ['token4_agent'])]
    assert cycle._get_carried(0, special_action_tokens) == ('token4_agent', 'token4_asset')

    agent = cycle.agents_manager.get_agent('token4_agent')
    asset = cycle.social_assets_manager.get_social_asset('token4_asset')

    assert agent.last_action == 'getCarried'
    assert asset.last_action == 'carry'
    assert agent.carried

    special_action_tokens = [('token4_agent', 'getCarried', ['']), ('token4_asset', 'carry', ['token4_agent'])]
    assert cycle._get_carried(0, special_action_tokens) == ('token4_agent', None)
    assert not agent.last_action_result


if __name__ == '__main__':
    test_connect_agent()
    test_connect_asset()
    test_disconnect_agent()
    test_disconnect_asset()
    test_get_agents_info()
    test_get_assets_info()
    test_get_step()
    test_activate_step()
    test_get_previous_steps()
    test_check_steps()
    test_update_steps()
    test_nothing_just_setup_for_pytest()
    test_check_abilities_and_resources()
    test_charge()
    test_charge_failed_param()
    test_charge_failed_location()
    test_move_agent()
    test_move_agent_failed_facility()
    test_move_agent_failed_less_parameters()
    test_move_agent_failed_more_parameters()
    test_move_agent_failed_battery()
    test_move_agent_failed_unable()
    test_move_asset()
    test_move_asset_failed_facility()
    test_move_asset_failed_less_parameters()
    test_move_asset_failed_more_parameters()
    test_move_asset_failed_unable()
    test_rescue_victim_agent()
    test_rescue_victim_agent_failed_param()
    test_rescue_victim_agent_failed_unknown()
    test_rescue_victim_asset()
    test_rescue_victim_asset_failed_param()
    test_rescue_victim_asset_failed_unknown()
    test_collect_water_agent()
    test_collect_water_agent_failed_param()
    test_collect_water_agent_failed_unknown()
    test_collect_water_asset()
    test_collect_water_asset_failed_param()
    test_collect_water_asset_failed_unknown()
    test_take_photo_agent()
    test_take_photo_agent_failed_param()
    test_take_photo_agent_failed_unknown()
    test_take_photo_asset()
    test_take_photo_asset_failed_param()
    test_take_photo_asset_failed_unknown()
    test_analyze_photo_agent()
    test_analyze_photo_agent_failed_param()
    test_analyze_photo_agent_failed_no_photos()
    test_analyze_photo_asset()
    test_analyze_photo_asset_failed_param()
    test_analyze_photo_asset_failed_no_photos()
    test_search_social_asset_agent()
    test_search_social_asset_agent_failed_param()
    test_search_social_asset_agent_failed_purpose()
    test_search_social_asset_agent_failed_no_assets()
    test_search_social_asset_asset()
    test_search_social_asset_asset_failed_param()
    test_search_social_asset_asset_failed_purpose()
    test_deliver_physical_agent()
    test_deliver_physical_agent_failed_less_param()
    test_deliver_physical_agent_failed_more_param()
    test_deliver_physical_agent_failed_more_param()
    test_deliver_physical_asset()
    test_deliver_physical_asset_failed_less_param()
    test_deliver_physical_asset_failed_more_param()
    test_deliver_physical_asset_failed_location()
    test_deliver_virtual_agent()
    test_deliver_virtual_agent_failed_less_param()
    test_deliver_virtual_agent_failed_more_param()
    test_deliver_virtual_agent_failed_location()
    test_deliver_virtual_asset()
    test_deliver_virtual_asset_failed_less_param()
    test_deliver_virtual_asset_failed_more_param()
    test_deliver_virtual_asset_failed_location()
    test_update_photos_state()
    test_carry()
    test_get_carried()
