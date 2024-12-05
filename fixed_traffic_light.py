import numpy as np

# Generate interarrival times (Poisson process)
def generate_interarrival_times(rate, duration):
    return np.random.exponential(1 / rate, int(duration * rate))


# Determine if the traffic light is green for a given direction at a specific time
def is_green_light(direction, time, green_ns, green_ew, yellow, cycle_time):
    cycle_position = time % cycle_time
    if direction == "NS":
        return cycle_position < green_ns
    elif direction == "EW":
        return green_ns + yellow <= cycle_position < cycle_time - yellow
    return False

# Simulate traffic light queue for a specific direction
def simulate_direction(arrivals, direction, green_time, yellow, cycle_time, service_time, simulation_time):
    waiting_times = []

    current_time = 0  # Tracks when the server (intersection) is free
    start_time = arrivals[0]
    for arrival_time in arrivals:
        # Check traffic light status
        cycle_position = max(arrival_time, start_time) % cycle_time
        is_green = is_green_light(direction, max(start_time, arrival_time), green_time, cycle_time - green_time, yellow,
                                  cycle_time)
        if is_green:
            start_time = max(arrival_time, current_time)
        else:
            red_and_yellow_wait = cycle_time - cycle_position if direction == "NS" else green_time - cycle_position
            start_time = max(arrival_time + red_and_yellow_wait, current_time + red_and_yellow_wait)

        end_time = start_time + service_time
        waiting_time = start_time - arrival_time
        if start_time > simulation_time:
            break

        waiting_times.append(waiting_time)
        # Update the current server availability time
        current_time = end_time

    return waiting_times

