from model import ProductionEnvironment, Event, Schedule

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
    