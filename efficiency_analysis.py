import fixed_traffic_light
import slotted_traffic_light
import numpy as np
import plotly.graph_objects as go
import math

simulation_time = 600
arrival_rate_ew = 0.1
green_ns = 30
yellow = 2
green_ew = 30
cycle_time = 64
service_time = 1

safety_time_same = 1
safety_time_same_with_delay = 1.5
total_slot_time = 8
total_slot_time_small = 4
safety_time_switch = 2
safety_time_switch_with_delay = 2.5
max_starvation_time = 24
max_starvation_time_small = 8

def generate_interarrival_times(rate, duration, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Set the seed for reproducibility
    interarrival_times = np.random.exponential(1 / rate, int(duration * rate * 1.5))  # Generate extra to ensure coverage
    cumulative_times = np.cumsum(interarrival_times)
    return cumulative_times[cumulative_times <= duration]  # Only include times within the simulation duration
arrival_rates = [3, 2.5, 2, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
# arrival_rates = [3]
# arrival_rates = [5, 3, 2.5, 2, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1, 0.9, 0.8, 0.7, 0.6, 0.5]

avg_waiting_ns = []
avg_waiting_ew = []
avg_waiting_overall = []

avg_capacity_ls = []
avg_capacity_ew = []
avg_total_capacity = []

# slotted
slotted_results_ns = []
slotted_results_ew = []
slotted_results_overall = []
slotted_results_with_delay = []

slotted_served_ls = []
slotted_served_with_delay = []
slotted_served_ns_ls = []
slotted_served_ew_ls = []

slotted_avg_waiting_time_ls = []
slotted_avg_waiting_time_ns_ls = []
slotted_avg_waiting_time_ew_ls = []

for arrival_rate in arrival_rates:
    results_ns = []
    results_ew = []
    results_overall = []
    served_ns = []
    served_ew = []
    total_served = []


    for _ in range(100):
        # Generate arrivals for both directions
        arrivals_ns = generate_interarrival_times(arrival_rate, simulation_time)
        arrivals_ew = generate_interarrival_times(arrival_rate_ew, simulation_time)

        #traffic light
        waiting_times_ns = fixed_traffic_light.simulate_direction(arrivals_ns, "NS", green_ns, yellow, cycle_time, service_time, simulation_time)
        waiting_times_ew = fixed_traffic_light.simulate_direction(arrivals_ew, "EW", green_ew, yellow, cycle_time, service_time, simulation_time)
        results_ns.append(np.mean(waiting_times_ns))
        results_ew.append(np.mean(waiting_times_ew))
        results_overall.append((sum(waiting_times_ns) + sum(waiting_times_ew)) / (len(waiting_times_ns) + len(waiting_times_ew)))

        served_ns.append(len(waiting_times_ns))
        served_ew.append(len(waiting_times_ew))
        total_served.append(len(waiting_times_ns) + len(waiting_times_ew))

    #traffic light
    # add to avg for arrival rates
    avg_waiting_ns.append(np.mean(results_ns))
    avg_waiting_ew.append(np.mean(results_ew))
    avg_waiting_overall.append(np.mean(results_overall))

    capacity_ns = np.mean(served_ns) / simulation_time
    capacity_ew = np.mean(served_ew) / simulation_time
    capacity_total = np.mean(total_served) / simulation_time
    avg_capacity_ls.append(capacity_ns)
    avg_capacity_ew.append(capacity_ew)
    avg_total_capacity.append(capacity_total)

    slotted_avg_waiting_ls = []
    slotted_avg_waiting_ls_with_delay = []

    slotted_avg_waiting_ns = []
    slotted_avg_waiting_ew = []

    slotted_avg_capacity_ls = []
    slotted_avg_capacity_ls_with_delay = []

    slotted_avg_capacity_ns = []
    slotted_avg_capacity_ew = []

    slotted_waiting_ns_ls = []
    slotted_waiting_ew_ls = []
    slotted_waiting_ls = []
    for _ in range(100):
        # Generate arrivals for both directions
        arrival_times_ns = generate_interarrival_times(arrival_rate, simulation_time)
        arrival_times_ew = generate_interarrival_times(arrival_rate_ew, simulation_time)
        # Simulate both directions
        slotted_avg_wait_ns, slotted_avg_wait_ew, slotted_served_ns, slotted_served_ew, wait_times_ns, wait_times_ew = slotted_traffic_light.simulate_slot_based_traffic(
            arrival_times_ns, arrival_times_ew, simulation_time, total_slot_time, safety_time_same, safety_time_switch,
            max_starvation_time
        )
        # Simulate both directions
        slotted_avg_wait_ns_d, slotted_avg_wait_ew_d, slotted_served_ns_d, slotted_served_ew_d, wait_times_ns_d, wait_times_ew_d = slotted_traffic_light.simulate_slot_based_traffic(
            arrival_times_ns, arrival_times_ew, simulation_time, total_slot_time, safety_time_same_with_delay,
            safety_time_switch_with_delay,
            max_starvation_time
        )
        slotted_results_ns.append(slotted_avg_wait_ns)
        slotted_results_ew.append(slotted_avg_wait_ew)
        slotted_results_overall.append(
            (slotted_avg_wait_ns * slotted_served_ns + slotted_avg_wait_ew * slotted_served_ew) / (
                        slotted_served_ns + slotted_served_ew))
        slotted_results_with_delay.append(
            (slotted_avg_wait_ns_d * slotted_served_ns_d + slotted_avg_wait_ew_d * slotted_served_ew_d) / (
                        slotted_served_ns_d + slotted_served_ew_d))

        slotted_served_ls.append(slotted_served_ns + slotted_served_ew)
        slotted_served_with_delay.append(slotted_served_ns_d + slotted_served_ew_d)
        slotted_served_ns_ls.append(slotted_served_ns)
        slotted_served_ew_ls.append(slotted_served_ew)

        traffic_light_served_ns = np.mean(served_ns)
        traffic_light_served_ew = np.mean(served_ew)
        slotted_waiting_ns_ls.append(np.mean(wait_times_ns[:math.floor(traffic_light_served_ns)]))
        slotted_waiting_ew_ls.append(np.mean(wait_times_ew[:math.floor(traffic_light_served_ew)]))
        slotted_waiting_ls.append(np.mean(wait_times_ns[:math.floor(traffic_light_served_ns)] + wait_times_ew[:math.floor(traffic_light_served_ew)]))

    # Calculate the average waiting times across all simulations
    slotted_avg_waiting_ls.append(np.mean(slotted_results_overall))
    slotted_avg_waiting_ls_with_delay.append(np.mean(slotted_results_with_delay))

    slotted_avg_waiting_ns.append(np.mean(slotted_results_ns))
    slotted_avg_waiting_ew.append(np.mean(slotted_results_ew))

    slotted_avg_capacity_ls.append(np.mean(slotted_served_ls) / simulation_time)
    slotted_avg_capacity_ls_with_delay.append(np.mean(slotted_served_with_delay) / simulation_time)

    slotted_avg_capacity_ns.append(np.mean(slotted_served_ns_ls) / simulation_time)
    slotted_avg_capacity_ew.append(np.mean(slotted_served_ew_ls) / simulation_time)

    slotted_avg_waiting_time_ls.append(np.mean(slotted_waiting_ls))
    slotted_avg_waiting_time_ns_ls.append(np.mean(slotted_waiting_ns_ls))
    slotted_avg_waiting_time_ew_ls.append(np.mean(slotted_waiting_ew_ls))

fig = go.Figure()

# fig.add_trace(go.Scatter(x=arrival_rates, y=avg_total_capacity, mode='lines+markers', name='Traffic Light'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_capacity_ls, mode='lines+markers', name='Slotted'))
# fig.update_layout(
#     title="Traffic Light System VS Slot-Based Solution : Average Capacity vs Arrival Rate",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Capacity (vehicles/sec)",
#     legend_title="Scenario",
# )

# fig.add_trace(go.Scatter(x=arrival_rates, y=avg_capacity_ls, mode='lines+markers', name='NS'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=avg_capacity_ew, mode='lines+markers', name='EW'))
# fig.update_layout(
#     title="Traffic Light System : Average Capacity NS vs EW",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Capacity (vehicles/sec)",
#     legend_title="Scenario",
# )
#
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_capacity_ns, mode='lines+markers', name='NS'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_capacity_ew, mode='lines+markers', name='EW'))
# fig.update_layout(
#     title="Slot-based System : Average Capacity NS vs EW",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Capacity (vehicles/sec)",
#     legend_title="Scenario",
# )

# fig.add_trace(go.Scatter(x=arrival_rates, y=avg_waiting_overall, mode='lines+markers', name='Traffic Light'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_time_ls, mode='lines+markers', name='Slot-based'))
# fig.update_layout(
#     title="Traffic Light VS Slot-based solution : Average Waiting Time",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Waiting Time (sec)",
#     legend_title="Scenario",
# )
#

# fig.add_trace(go.Scatter(x=arrival_rates, y=avg_waiting_ns, mode='lines+markers', name='NS'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=avg_waiting_ew, mode='lines+markers', name='EW'))
# fig.update_layout(
#     title="Traffic Light : Average Waiting Time NS vs EW",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Waiting Time (sec)",
#     legend_title="Scenario",
# )

# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_time_ns_ls, mode='lines+markers', name='NS'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_time_ew_ls, mode='lines+markers', name='EW'))
# fig.update_layout(
#     title="Slot-based Solution : Average Waiting Time NS vs EW",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Waiting Time (sec)",
#     legend_title="Scenario",
# )

# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_ls, mode='lines+markers', name='no Delay'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_ls_with_delay, mode='lines+markers', name='Delay'))
# fig.update_layout(
#     title="Slot-based : Average Waiting Time without Delay VS with Delay",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Waiting Time (sec)",
#     legend_title="Scenario",
# )
#
#
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_capacity_ls, mode='lines+markers', name='no Delay'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_capacity_ls_with_delay, mode='lines+markers', name='Delay'))
# fig.update_layout(
#     title="Slot-based : Average Capacity without Delay VS with Delay",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Capacity (vehicles/sec)",
#     legend_title="Scenario",
# )
#

# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_ls_with_delay, mode='lines+markers', name='slot_time: 4'))
# fig.add_trace(go.Scatter(x=arrival_rates, y=slotted_avg_waiting_ls, mode='lines+markers', name='slot_time: 8'))
# fig.update_layout(
#     title="Slot-based : Average Waiting Time With Slot Time 8 vs 4",
#     xaxis_title="Arrival Rate (vehicles/sec)",
#     yaxis_title="Average Waiting Time (sec)",
#     legend_title="Scenario",
# )

# fig.show()