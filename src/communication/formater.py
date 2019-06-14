import json

SIMULATION_STARTED_EVENT = 'simulation_started'
JOB_RESULT_EVENT = 'job_result'
SIMULATION_ENDED_EVENT = 'simulation_ended'


def format_for_event(event, agent, simulation_state):
    if event == SIMULATION_STARTED_EVENT:
        value = {'simulation_started': True}

    elif event == JOB_RESULT_EVENT:
        value = {
            'agent': agent,
            'map_perceptions': simulation_state['map_perceptions'],
            'events': {
                'current_event': simulation_state['current_event'],
                'pending_events': simulation_state['pending_events']
            }
        }

    elif event == SIMULATION_ENDED_EVENT:
        value = {'simulation_ended': True}

    else:
        return None

    return json.dumps(value)
