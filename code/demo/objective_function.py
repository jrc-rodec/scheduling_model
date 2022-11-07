from models import SimulationEnvironment
from models import Order, Schedule, SimulationEnvironment

def get_first(schedule : Schedule, order : Order):
    first = (-1, float('inf'))
    assigned_workstation = None
    for workstation in schedule.assignments:
        for assignment in schedule.assignments[workstation]:
            if assignment[2].id == order.id:
                if assignment[1] < first[1]:
                    first = assignment
                    assigned_workstation = workstation
    # return assignment + workstation
    first, assigned_workstation

def get_last(schedule : Schedule, order : Order, environment : SimulationEnvironment):
    last = (-1, 0)
    assigned_workstation = None
    for workstation in schedule.assignments:
        for assignment in schedule.assignments[workstation]:
            if assignment[2].id == order.id:
                duration = environment.get_duration(assignment[0], workstation)
                if assignment[1] + duration > last[1]:
                    last = assignment
                    assigned_workstation = workstation
    # return assignment + workstation
    return last, assigned_workstation

def makespan(schedule : Schedule, env : SimulationEnvironment):
    min = float('inf')
    max = 0
    # find first
    for workstation in schedule.assignments:
        for assignment in schedule.assignments[workstation]:
            if assignment[1] < min:
                min = assignment[1]
            if assignment[1] + env.get_duration(assignment[0], workstation) > max:
                max = assignment[1] + env.get_duration(assignment[0], workstation)
    return max - min

def min_tardiness(schedule : Schedule, orders, environment : SimulationEnvironment):
    sum = 0
    # for each order, find last task
    for order in orders:
        last_assignment, workstation = get_last(schedule, order, environment)
        duration = environment.get_duration(last_assignment[0], workstation)
        start = last_assignment[1]
        end = start + duration
        if end > order.delivery_time:
            # sum all delays
            sum += end - order.delivery_time
    return sum

def min_deviation(schedule : Schedule, orders, environment : SimulationEnvironment):
    sum = 0
    # for each order, find last task
    for order in orders:
        last_assignment, workstation = get_last(schedule, order, environment)
        duration = environment.get_duration(last_assignment[0], workstation)
        start = last_assignment[1]
        end = start + duration
        # sum all delays
        sum += abs(end - order.delivery_time)
    return sum

def min_idle_time(schedule : Schedule, environment : SimulationEnvironment):
    unused_workstations = 0
    last_timeslot = 0
    idle_time = 0
    # for each workstation, sum idle times
    for workstation in environment.workstations:
        if workstation.id in schedule.assignments:
            slots = []
            for assignment in schedule.assignments[workstation.id]:
                start = assignment[1]
                duration = environment.get_duration(assignment[0], workstation.id)
                end = start + duration
                slots.append((start, end))
                if end > last_timeslot:
                    last_timeslot = end
            sorted_slots = sorted(slots, key=lambda x: x[0])
            last_end = 0
            for slot in sorted_slots:
                idle_time += slot[0] - last_end
                last_end = slot[1]
        else:
            unused_workstations += 1
    # add idle time of completely unused workstations
    idle_time += unused_workstations * last_timeslot
    return idle_time

def max_profit(schedule : Schedule, orders, environment : SimulationEnvironment):
    profit = 0
    # sum profits of all scheduled orders
    for order in orders:
        payment_amount = order.payment_amount
        #for resource in order.resources:
        #    payment_amount += resource[2]
        profit += payment_amount # order.payment_amount
        assignment, workstation = get_last(schedule, order, environment)
        duration = environment.get_duration(assignment[0], workstation)
        end = assignment[1] + duration
        penalty = 0
        if end > order.latest_acceptable_time:
            penalty += order.penalty
        elif end > order.delivery_time:
            penalty += order.tardiness_fee
        profit -= penalty
    # subtract all delay fees, subtract all penalties for unscheduled orders
    return profit

# implement additional functions here

def calculate_comparison_values(schedule : Schedule, orders, environment : SimulationEnvironment):
    # NOTE: unscheduled orders are currently not accounted for in these functions
    makespan_fitness = makespan(schedule, environment)
    tardiness_fitness = min_tardiness(schedule, orders, environment)
    deviation_fitness = min_deviation(schedule, orders, environment)
    #tardiness_fitness = float('inf')
    #deviation_fitness = float('inf')
    idle_time_fitness = min_idle_time(schedule, environment)
    #idle_time_fitness = float('inf')
    profit_fitness = max_profit(schedule, orders, environment)
    #profit_fitness = float('inf')
    # add additional functions here
    return makespan_fitness, tardiness_fitness, deviation_fitness, idle_time_fitness, profit_fitness