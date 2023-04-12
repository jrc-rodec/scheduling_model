import random
import copy

class Particle:

    def __init__(self):
        self.best_positions : list[int] = []
        self.best_fitness : float = float('inf')
        self.velocities : list[float] = []
        self.current_positions : list[int] = []
        self.current_fitness : float = float('inf')

    def update(self) -> None:
        if self.current_fitness < self.best_fitness:
            self.best_positions = copy.deepcopy(self.current_positions)
            self.best_fitness = self.current_fitness


class PSO:

    def get_best(self, particles : list[Particle]) -> Particle:
        best = particles[0]
        for particle in particles:
            if particle.best_fitness < best.best_fitness:
                best = particle
        return best

    def evaluate(self, particle : Particle) -> None:
        sum = 0
        for position in particle.current_positions:
            sum += position
        particle.current_fitness = sum
        particle.update()

    def create_particle(self, dimensions : int = 5, lower_bounds : list[int] = [], upper_bounds : list[int] = []) -> Particle:
        positions : list[int] = []
        velocities : list[float] = []
        for i in range(dimensions):
            positions.append(random.randint(lower_bounds[i], upper_bounds[i]))
            velocities.append(0.0)
        particle : Particle = Particle()
        particle.current_positions = positions
        particle.velocities = velocities
        return particle

    def optimize(self, particle_amount : int = 10, dimensions : int = 5, lower_bounds : list[int] = [], upper_bounds : list[int] = [], max_generation : int = 100, personal_weight : float = 0.2, global_weight : float = 0.5, inertia : float = 0.2, max_velocity : float = 2.0, min_velocity : float = 0.5):
        particles : list[Particle] = []
        for _ in range(particle_amount):
            particle : Particle = self.create_particle(dimensions, lower_bounds, upper_bounds)
            self.evaluate(particle)
            particles.append(particle)
        for generation in range(max_generation):
            current_best = self.get_best(particles)
            for particle in particles:
                for i in range(dimensions):
                    r_personal = random.uniform(0, 1)
                    r_global = random.uniform(0, 1)
                    velocity = inertia * particle.velocities[i] + personal_weight * r_personal * (particle.best_positions[i] - particle.current_positions[i]) + global_weight * r_global * (current_best.best_positions[i] - particle.current_positions[i])
                    if velocity > max_velocity:
                        velocity = max_velocity
                    elif velocity < min_velocity:
                        velocity = min_velocity
                    particle.current_positions[i] += velocity
                    particle.velocities[i] = velocity
                    if particle.current_positions[i] > upper_bounds[i]:
                        particle.current_positions[i] = upper_bounds[i]
                    elif particle.current_positions[i] < lower_bounds[i]:
                        particle.current_positions[i] = lower_bounds[i]
                    #particle.current_positions[i] = int(particle.current_positions[i]) # clip to integers
                self.evaluate(particle)
        current_best = self.get_best(particles)
        return current_best

pso = PSO()
particle : Particle = pso.optimize(particle_amount=50, dimensions=5, lower_bounds=[0] * 5, upper_bounds=[2] * 5, max_generation=100, personal_weight=0.5, global_weight=0.6, inertia=0.7)
print(particle.best_positions)
print(particle.best_fitness)

