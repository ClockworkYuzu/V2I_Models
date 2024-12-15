import numpy as np
from collections import deque

# Generate interarrival times (Poisson process)
def generate_interarrival_times(rate, duration, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Set the seed for reproducibility
    interarrival_times = np.random.exponential(1 / rate, int(duration * rate))
    return np.cumsum(interarrival_times).astype(int)  # Convert to cumulative integer arrival times

# Serve vehicles in a direction
def serve_vehicles(arrivals, allocated_time, current_time, waiting_time_in_ahead, safety_time_same):
    current_time += waiting_time_in_ahead
    total_wait_time = 0
    vehicles_served = 0
    slot_end_time = current_time + allocated_time
    wait_times = []

    while arrivals and current_time <= slot_end_time:
        arrival_time = arrivals[0]
        if arrival_time <= current_time:
            arrivals.popleft()
            wait_time = current_time - arrival_time  # Calculate waiting time
            total_wait_time += wait_time
            wait_times.append(wait_time)
            vehicles_served += 1
            current_time += safety_time_same  # Move time forward as vehicle crosses
        elif arrival_time < slot_end_time:
            arrivals.popleft()
            vehicles_served += 1
            wait_times.append(0)
            current_time = arrival_time + safety_time_same
        else:
            break

    return max(current_time, slot_end_time), total_wait_time, vehicles_served, wait_times

# Simulate the slot-based traffic light system
def simulate_slot_based_traffic(arrival_times_ns, arrival_times_ew, simulation_time, total_slot_time, safety_time_same, safety_time_switch, max_starvation_time):
    # Convert arrival times to queues
    arrivals_ns = deque(arrival_times_ns)
    arrivals_ew = deque(arrival_times_ew)
    # print(arrivals_ns)
    # print(arrivals_ew)
    wait_times_ns = []
    wait_times_ew = []

    current_time = 0
    total_wait_time_ns = total_wait_time_ew = 0
    vehicles_served_ns = vehicles_served_ew = 0
    last_service_ns = 0
    last_service_ew = 0
    last_direction = None  # Track the last served direction

    while current_time < simulation_time:
        waiting_ns = [arrival for arrival in arrivals_ns if arrival <= current_time]
        waiting_ew = [arrival for arrival in arrivals_ew if arrival <= current_time]

        # Calculate weights based on waiting vehicle counts
        total_waiting = len(waiting_ns) + len(waiting_ew)
        if total_waiting > 0:
            weight_ns = len(waiting_ns) / total_waiting
            weight_ew = len(waiting_ew) / total_waiting
        else:
            # No vehicles waiting, idle slot
            weight_ns = weight_ew = 0.5

        # Check for starvation
        time_since_ns = current_time - last_service_ns
        time_since_ew = current_time - last_service_ew

        if time_since_ns >= max_starvation_time and len(waiting_ns) >= 1:
            # Prioritize NS direction
            time_ns, time_ew = total_slot_time, 0
        elif time_since_ew >= max_starvation_time and len(waiting_ew) >= 1:
            # Prioritize EW direction
            time_ns, time_ew = 0, total_slot_time
        else:
            # Allocate time proportionally
            # time_ns = weight_ns * total_slot_time
            time_ns = int(round(weight_ns * total_slot_time))
            time_ew = total_slot_time - time_ns

        # Serve NS direction
        if time_ns > 0:
            # Determine if safety_time_switch is required
            if last_direction == "EW" and current_time > 0:
                time_since_last_vehicle = current_time - max(last_service_ew, 0)
                safety_time = max(0, safety_time_switch - time_since_last_vehicle)
            else:
                safety_time = 0

            current_time, wait_time_ns, served_ns, wait_times_new = serve_vehicles(
                arrivals_ns, time_ns, current_time, safety_time, safety_time_same
            )

            for time in wait_times_new:
                wait_times_ns.append(time)

            total_wait_time_ns += wait_time_ns
            vehicles_served_ns += served_ns
            last_service_ns = current_time

        # Serve EW direction
        if time_ew > 0:
            # Determine if safety_time_switch is required
            if last_direction == "NS" and current_time > 0:
                time_since_last_vehicle = current_time - max(last_service_ns, 0)
                safety_time = max(0, safety_time_switch - time_since_last_vehicle)
            else:
                safety_time = 0

            current_time, wait_time_ew, served_ew, wait_times_new = serve_vehicles(
                arrivals_ew, time_ew, current_time, safety_time, safety_time_same
            )

            for time in wait_times_new:
                wait_times_ew.append(time)

            total_wait_time_ew += wait_time_ew
            vehicles_served_ew += served_ew
            last_service_ew = current_time

        # Update the last direction
        last_direction = "NS" if time_ns > time_ew else "EW"

    # Calculate average waiting times
    avg_wait_time_ns = total_wait_time_ns / vehicles_served_ns if vehicles_served_ns else 0
    avg_wait_time_ew = total_wait_time_ew / vehicles_served_ew if vehicles_served_ew else 0

    return avg_wait_time_ns, avg_wait_time_ew, vehicles_served_ns, vehicles_served_ew, wait_times_ns, wait_times_ew