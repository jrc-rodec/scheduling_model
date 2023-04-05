from model import ProductionEnvironment, Event, Schedule, Assignment
import copy 

class Uncertainty:

    NEXT_ID : int = 0

    def __init__(self):
        self.id : int = Uncertainty.NEXT_ID
        Uncertainty.NEXT_ID += 1

    def generate(self, start_time : int = 0, end_time : int = 0, schedule : Schedule = None, production_environment : ProductionEnvironment = None) -> list[Event]:
        pass

class EpistemicUncertainty(Uncertainty):
    
    def __init__(self):
        super().__init__()
        self.data = []

class AleatoricUncertainty(Uncertainty):

    def __init__(self):
        super().__init__()
        self.probability_distribution = None

class ScenarioGenerator:

    def __init__(self):
        self.uncertainties : list[Uncertainty] = []

    def register_uncertainty(self, uncertainty : Uncertainty) -> None:
        self.uncertainties.append(uncertainty)

    def generate_scenario(self, start_time : int = 0, end_time : int = 0, schedule : Schedule = None, production_environment : ProductionEnvironment = None) -> list[Event]:
        events : list[Event] = []
        for uncertainty in self.uncertainties:
            events.extend(uncertainty.generate(start_time, end_time, schedule, production_environment))
        return events
    
    def generate_scenario_for_schedule(self, end_time : int):
        for i in range(end_time):
            for uncertainty in self.uncertainties:
                # check for each time step 
                pass


    def measure_robustness(self, amount : int, schedule : Schedule, production_environment : ProductionEnvironment):
        for i in range(amount):
            # generate scenario
            events : list[Event] = self.generate_scenario()
            events.sort(key=lambda x: x.get_parameter('start_time')) # apply the events in order
            # apply scenario
            simulated_schedule = copy.deepcopy(schedule)
            for event in events:
                start = event.get_parameter('start_time')
                end = event.get_parameter('end_time')
                duration = end - start
                event_type = production_environment.get_event(event.get_parameter('event_type'))
                if event_type == 'workstation breakdown':
                    workstation = production_environment.get_workstation(event.get_parameter('workstation'))
                    assignments : list[Assignment] = []
                    # find and shift all affected assignments
                    # check if the breakdown affects anything
                    immediately_affected_assignments : list[Assignment] = simulated_schedule.get_assignments_on_workstation_between(workstation.id, start, start+duration)
                    if len(immediately_affected_assignments) > 0:
                        # all assignments on the same workstation after the start time (and during)
                        assignments.extend(immediately_affected_assignments) # NOTE: might have some overlap with active
                        active_assignments : list[Assignment] = simulated_schedule.get_active_assignments_on_workstation(workstation.id, start)
                        for assignment in active_assignments:
                            if assignment not in assignments:
                                assignments.append(assignment)
                        planned_assignments : list[Assignment] = simulated_schedule.get_assignments_on_workstation_after(workstation.id, start)
                        for assignment in planned_assignments:
                            if assignment not in assignments:
                                assignments.append(assignment)
                        # all assignments on other workstations which need to be in sequence with the affected assignments on the workstations, and all assignments on the workstations of these assignments after them
                        
                        # apply the right shift TODO: take idle times into account, remove idle times from necessary delay
                        for assignment in assignments:
                            assignment.start_time += duration
                            assignment.end_time += duration
                    # ...
                elif event_type == 'resource unavailable':
                    resource = production_environment.get_resource(event.get_parameter('resource'))
                    # find and shift all affected assignments
                    # ...
                    
                # ... TODO: handle other cases
            # evaluate schedule