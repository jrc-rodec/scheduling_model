#pragma once
#include <vector>
#include <random>
#include <limits>
#include <algorithm>
#include <iostream>
#include "RandomGenerator.h"

struct Gap {
	int start = 0;
	int end = 0;
	int next = 0;
};

class Individual {
private:
	std::vector<int>* REQUIRED_OPERATIONS;
	std::vector<std::vector<int>>* AVAILABLE_WORKSTATIONS;
	std::vector<std::vector<int>>* AVAILABLE_WORKERS;
	std::vector<std::vector<int>>* BASE_DURATIONS;
	std::vector<int>* JOBS;
	RandomGenerator rng;
	std::vector<float> _min_distance_success;

	int _initialization_attempts = 100;
	double _distance_adjustment_rate = 0.75;

	double _fitness;
	std::vector<int> _workers;
	std::vector<int> _workstations;
	std::vector<int> _sequence;
	std::vector<int> _durations;

private:
	int getMaxDissimilarity() const {
		int workstationSum = 0;
		std::vector<std::vector<int>> availableWorkstations = *AVAILABLE_WORKSTATIONS;
		std::vector<int> requiredOperations = *REQUIRED_OPERATIONS;
		for (size_t i = 0; i < availableWorkstations.size(); i++) {
			workstationSum += availableWorkstations[i].size();
		}
		return requiredOperations.size() + workstationSum;
	}
	int getDissimilarity(const Individual& other) const {
		int dissimilarity = 0;
		for (size_t i = 0; i < _sequence.size(); i++) {
			dissimilarity += _sequence[i] != other._sequence[i];
		}
		for (size_t i = 0; i < _workstations.size(); i++) {
			if (_workstations[i] != other._workstations[i]) {
				dissimilarity += AVAILABLE_WORKSTATIONS[i].size();
			}
		}
		return dissimilarity;
	}
	float getAverageDissimilarity(const std::vector<Individual>& population) const {
		int dissimilaritySum = 0;
		for (size_t i = 0; i < population.size(); i++) {
			dissimilaritySum += getDissimilarity(population[i]);
		}
		return ((float)(dissimilaritySum) / population.size());
	}
	void adjustIndividual() {
		std::vector<std::vector<Gap>> gaps;
		std::vector<int> availableWorkstations;
		std::vector<std::vector<int>> baseDurations = *BASE_DURATIONS;
		std::vector<int> requiredOperations = *REQUIRED_OPERATIONS;
		std::vector<int> jobs = *JOBS;
		int nWorkstations = baseDurations.size();
		std::vector<int> endTimesOnWorkstations;
		std::vector<int> endTimesOfOperations;
		std::vector<int> nextOperation;

		for (size_t i = 0; i < nWorkstations; i++) {
			if (!std::count(availableWorkstations.begin(), availableWorkstations.end(), i)) {
				availableWorkstations.push_back(i);
			}
			gaps.push_back(std::vector<Gap>());
			endTimesOnWorkstations.push_back(0);
		}
		for (size_t i = 0; i < requiredOperations.size(); i++) {
			endTimesOfOperations.push_back(0);
		}
		for (size_t i = 0; i < jobs.size(); i++) {
			nextOperation.push_back(0);
		}

		for (size_t i = 0; i < _sequence.size(); i++) {
			//int job = _sequence[i];
			//int operation = nextOperation[i];
			int operationIndex = 0;
			int j = 0;
			while (j < requiredOperations.size() && requiredOperations[j] != _sequence[i]) {
				j++;
			}
			operationIndex = j + nextOperation[_sequence[i]];
			int workstation = _workstations[operationIndex];
			nextOperation[_sequence[i]]++;
			int duration = _durations[operationIndex];
			bool inserted = false;
			for (size_t g = 0; g < gaps[workstation].size() && !inserted; g++) {
				Gap gap = gaps[workstation][g];
				if (gap.end - gap.start >= duration) {
					// found a gap
					if (operationIndex == 0 || (requiredOperations[operationIndex - 1] == requiredOperations[operationIndex] && endTimesOfOperations[operationIndex - 1] <= gap.end - duration)) {
						inserted = true;
						int start = operationIndex == 0 ? 0 : std::min(gap.start, endTimesOfOperations[operationIndex - 1]);
						int end = start + duration;
						if (gap.end - end > 0) {
							Gap g_new;
							g_new.start = end;
							g_new.end = gap.end;
							g_new.next = operationIndex;
							gaps[workstation].push_back(g_new);
						}
						endTimesOfOperations[operationIndex] = end;
						int jobSwap = requiredOperations[gap.next];
						int swapOperationIndex = 0;
						int swapStartIndex = 0;
						int k = 0;
						while (k < requiredOperations.size() && requiredOperations[k] != jobSwap) {
							k++;
						}
						swapStartIndex = k;
						swapOperationIndex = gap.next - swapStartIndex;
						int count = 0;
						int swapIndividualIndex = 0;
						bool found = false;
						for (size_t l = 0; l < _sequence.size() && !found; l++) {
							if (_sequence[l] == jobSwap) {
								if (count == swapOperationIndex) {
									swapIndividualIndex = l;
									found = true;
								}
								count++;
							}
						}
						int tmp = _sequence[swapIndividualIndex];
						_sequence[swapIndividualIndex] = _sequence[i];
						_sequence[i] = tmp;

						gaps[workstation].erase(gaps[workstation].begin() + g);
					}
				}
			}
			if (!inserted) {
				int jobMinStart = 0;
				if (operationIndex != 0 && requiredOperations[operationIndex - 1] == requiredOperations[operationIndex]) {
					jobMinStart = endTimesOfOperations[operationIndex - 1];
				}
				if (jobMinStart > endTimesOnWorkstations[workstation]) {
					Gap g_new;
					g_new.start = jobMinStart;
					g_new.end = jobMinStart + duration;
					g_new.next = operationIndex;
					gaps[workstation].push_back(g_new);
					endTimesOnWorkstations[workstation] = jobMinStart + duration;
				}
				else {
					endTimesOnWorkstations[workstation] += duration;
				}
				endTimesOfOperations[operationIndex] = endTimesOnWorkstations[workstation];
			}
		}
	}

public:
	Individual(){
		rng = RandomGenerator();
		_fitness = std::numeric_limits<double>::max();
	}
	Individual(std::vector<int>* requiredOperations, std::vector<std::vector<int>>* availableWorkstations, std::vector<std::vector<int>>* availableWorkers, std::vector<std::vector<int>>* baseDurations, std::vector<int>* jobs) : Individual() {
		REQUIRED_OPERATIONS = requiredOperations;
		AVAILABLE_WORKSTATIONS = availableWorkstations;
		AVAILABLE_WORKERS = availableWorkers;
		BASE_DURATIONS = baseDurations;
		JOBS = jobs;
	}
	Individual(const Individual& other) : Individual(other.REQUIRED_OPERATIONS, other.AVAILABLE_WORKSTATIONS, other.AVAILABLE_WORKERS, other.BASE_DURATIONS, other.JOBS) {
		_workstations = other._workstations;
		_workers = other._workers;
		_sequence = other._sequence;
		_durations = other._durations;
		_fitness = other._fitness;
		REQUIRED_OPERATIONS = other.REQUIRED_OPERATIONS;
		AVAILABLE_WORKSTATIONS = other.AVAILABLE_WORKSTATIONS;
		AVAILABLE_WORKERS = other.AVAILABLE_WORKERS;
		BASE_DURATIONS = other.BASE_DURATIONS;
		JOBS = other.JOBS;
	}
	Individual(const Individual& parentA, const Individual& parentB, const std::vector<int>& parentSplit, std::vector<int>* requiredOperations, std::vector<std::vector<int>>* availableWorkstations, std::vector<std::vector<int>>* availableWorkers, std::vector<std::vector<int>>* baseDurations, std::vector<int>* jobs) : Individual(requiredOperations, availableWorkstations, availableWorkers, baseDurations, jobs) {
		// uniform crossover
		// parent_split is only for the sequence
		std::vector<int> operations = *jobs;
		std::vector<int> setA;
		std::vector<int> setB;
		for (size_t i = 0; i < parentSplit.size(); i++) {
			if (parentSplit[i]) {
				setB.push_back(operations[i]);
			}
			else {
				setA.push_back(operations[i]);
			}
		}
		int b_index = 0;
		std::vector<int> parent_b_values;
		for (size_t i = 0; i < parentB._sequence.size(); i++) {
			if (std::count(setB.begin(), setB.end(), parentB._sequence[i])) {
				parent_b_values.push_back(parentB._sequence[i]);
			}
		}
		for (size_t i = 0; i < parentA._sequence.size(); i++) {
			if (std::count(setA.begin(), setA.end(), parentA._sequence[i])) {
				_sequence.push_back(parentA._sequence[i]);
			}
			else {
				_sequence.push_back(parent_b_values[b_index]);
				b_index++;
			}
		}
		// workstation crossover
		std::vector<int> split;
		for (size_t i = 0; i < parentA._workstations.size(); i++) {
			if (rng.randomDouble() < 0.5) {
				_workstations.push_back(parentA._workstations[i]);
				_durations.push_back(parentA._durations[i]);
			}
			else {
				_workstations.push_back(parentB._workstations[i]);
				_durations.push_back(parentB._durations[i]);
			}
		}
	}
	Individual(std::vector<Individual>& population, std::vector<int>* requiredOperations, std::vector<std::vector<int>>* availableWorkstations, std::vector<std::vector<int>>* availableWorkers, std::vector<std::vector<int>>* baseDurations, std::vector<int>* jobs) : Individual(requiredOperations, availableWorkstations, availableWorkers, baseDurations, jobs) {
		float dissimilarity = 0;
		float minDistance = getMaxDissimilarity();
		int attempts = 0;
		std::vector<int> operations = *REQUIRED_OPERATIONS;
		std::vector<std::vector<int>> workstations = *AVAILABLE_WORKSTATIONS;
		std::vector<std::vector<int>> durations = *BASE_DURATIONS;
		_sequence = operations;
		while (dissimilarity < minDistance) {
			if (attempts > _initialization_attempts) {
				minDistance *= 0.75f;
				attempts = 0;
			}
			std::shuffle(_sequence.begin(), _sequence.end(), rng.rng);
			_workstations.clear();
			for (size_t i = 0; i < workstations.size(); i++) {
				_workstations.push_back(workstations[i][rng.randomInteger(0, workstations[i].size()-1)]);
			}
			for (size_t i = 0; i < workstations.size(); i++) {
				_durations.push_back(durations[i][_workstations[i]]);
			}
			adjustIndividual();
			dissimilarity = getAverageDissimilarity(population);
			attempts++;
		}
		
	}

	~Individual(){}

	bool operator==(const Individual& other) const {
		for (size_t i = 0; i < _workstations.size(); i++) {
			if (other._workstations[i] != _workstations[i]) {
				return false;
			}
		}
		for (size_t i = 0; i < _sequence.size(); i++) {
			if (other._sequence[i] != _sequence[i]) {
				return false;
			}
		}
		return true;
	}
	bool operator!=(const Individual& other) const {
		for (size_t i = 0; i < _workstations.size(); i++) {
			if (other._workstations[i] != _workstations[i]) {
				return true;
			}
		}
		for (size_t i = 0; i < _sequence.size(); i++) {
			if (other._sequence[i] != _sequence[i]) {
				return true;
			}
		}
		return false;
	}
	void operator=(const Individual& other) {
		_workstations = other._workstations;
		_workers = other._workers;
		_sequence = other._sequence;
		_durations = other._durations;
		_fitness = other._fitness;
	}
	bool operator<(const Individual& other) const {
		return _fitness < other._fitness;
	}
	bool operator<=(const Individual& other) const {
		return _fitness <= other._fitness;
	}
	bool operator>(const Individual& other) const {
		return _fitness > other._fitness;
	}
	bool operator>=(const Individual& other) const {
		return _fitness >= other._fitness;
	}

	double getFitness() const {
		return _fitness;
	}
	void evaluate() {
		std::vector<int> nextOperation;
		std::vector<int> endOnWorkstations;
		std::vector<int> endTimes;
		std::vector<int> jobs = *JOBS;
		std::vector<int> requiredOperations = *REQUIRED_OPERATIONS;
		std::vector<std::vector<int>> baseDurations = *BASE_DURATIONS;
		for (size_t i = 0; i < jobs.size(); i++) {
			nextOperation.push_back(0);
		}
		for (size_t i = 0; i < baseDurations[0].size(); i++) {
			endOnWorkstations.push_back(0);
		}
		for (size_t i = 0; i < requiredOperations.size(); i++) {
			endTimes.push_back(-1);
		}
		for (size_t i = 0; i < _sequence.size(); i++) {
			int operation = nextOperation[_sequence[i]];
			int j = 0;
			while (j < requiredOperations.size() && requiredOperations[j] != _sequence[i]) {
				j++;
			}
			int startIndex = j + operation;
			nextOperation[_sequence[i]]++;
			int workstation = _workstations[startIndex];
			int duration = _durations[startIndex];
			int offset = 0;
			int minStartJob = 0;
			if (operation > 0) {
				offset = std::max(0, endTimes[startIndex - 1] - endOnWorkstations[workstation]);
				minStartJob = endTimes[startIndex - 1];
			}
			endTimes[startIndex] = endOnWorkstations[workstation] + duration + offset;
			endOnWorkstations[workstation] = endTimes[startIndex];
		}
		_fitness = *std::max_element(endTimes.begin(), endTimes.end());
	}
	void mutate(float p = 0.0f) {
		if (p == 0.0f) {
			p = 1 / (_sequence.size() + _workstations.size());
		}
		for (size_t i = 0; i < _sequence.size(); i++) {
			if (rng.randomDouble() < p) {
				// swap
				int swapWith = rng.randomInteger(0, _sequence.size()-1);
				if (swapWith == i) {
					swapWith = (swapWith + 1) % _sequence.size();
				}
				int tmp = _sequence[i];
				_sequence[i] = _sequence[swapWith];
				_sequence[swapWith] = tmp;
			}
		}
		std::vector<std::vector<int>> availableWorkstations = *AVAILABLE_WORKSTATIONS;
		std::vector<std::vector<int>> baseDurations = *BASE_DURATIONS;
		for (size_t i = 0; i < _workstations.size(); i++) {
			if (rng.randomDouble() < p && availableWorkstations[i].size() > 1) {
				int original = _workstations[i];
				int new_workstation = rng.randomInteger(0, availableWorkstations[i].size()-1);
				if (availableWorkstations[i][new_workstation] == original) {
					new_workstation = (new_workstation + 1) % availableWorkstations[i].size();
				}
				_workstations[i] = availableWorkstations[i][new_workstation];
				_durations[i] = baseDurations[i][new_workstation];
			}
		}
		adjustIndividual();
	}
	void copy(Individual& other) {
		_fitness = other._fitness;
		_workers = other._workers;
		_workstations = other._workstations;
		_sequence = other._sequence;
		_durations = other._durations;
		REQUIRED_OPERATIONS = other.REQUIRED_OPERATIONS;
		AVAILABLE_WORKSTATIONS = other.AVAILABLE_WORKSTATIONS;
		AVAILABLE_WORKERS = other.AVAILABLE_WORKERS;
		BASE_DURATIONS = other.BASE_DURATIONS;
		JOBS = other.JOBS;
	}
};

class GA
{
private:
	RandomGenerator rng;
	std::vector<int> _jobs;

	std::vector<int> REQUIRED_OPERATIONS;
	std::vector<std::vector<int>> AVAILABLE_WORKSTATIONS;
	std::vector<std::vector<int>> AVAILABLE_WORKERS;
	std::vector<std::vector<int>> BASE_DURATIONS;
	std::vector<int> JOBS;

	int _tournamentSize = 2;

	int select(const std::vector<Individual>& population) {
		// tournament selection
		if (_tournamentSize == 0) {
			_tournamentSize = int((population.size()) / 10);
		}
		std::vector<int> participants;
		for (size_t i = 0; i < _tournamentSize; i++) {
			int next = 0;
			do {
				next = rng.randomInteger(0, population.size()-1);
			} while (std::count(participants.begin(), participants.end(), next));
			participants.push_back(next);
		}
		int min = std::numeric_limits<int>::max();;
		int min_index = 0;
		for (size_t i = 0; i < participants.size(); i++) {
			if (population[participants[i]].getFitness() < min) {
				min = population[participants[i]].getFitness();
				min_index = participants[i];
			}
		}
		return min_index;
	}

	void recombine(std::vector<Individual>& population, Individual* oA, Individual* oB) {
		// recombine
		int parentA = select(population);
		int parentB;
		int counter = 0;
		do {
			parentB = select(population);
			counter++;
		} while (parentA == parentB && counter < 10);
		std::vector<int> split;
		for (size_t i = 0; i < _jobs.size(); i++) {
			split.push_back(rng.randomDouble() < 0.5f);
		}
		Individual offspringA = Individual(population[parentA], population[parentB], split, &REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
		Individual offspringB = Individual(population[parentB], population[parentA], split, &REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
		oA->copy(offspringA);
		oB->copy(offspringB);
	}

	float averageFitness(std::vector<Individual>& population) {
		int sum = 0;
		for (size_t i = 0; i < population.size(); i++) {
			sum += population[i].getFitness();
		}
		return (float)sum / population.size();
	}

public:
	GA() {
		rng = RandomGenerator();
	}

	GA(std::vector<int> jobs, std::vector<std::vector<int>> workstationsPerOperation, std::vector<std::vector<int>> baseDurations) : GA() {
		REQUIRED_OPERATIONS = jobs;
		AVAILABLE_WORKSTATIONS = workstationsPerOperation;
		BASE_DURATIONS = baseDurations;
		for (size_t i = 0; i < jobs.size(); i++) {
			if (!std::count(_jobs.begin(), _jobs.end(), jobs[i])) {
				_jobs.push_back(jobs[i]);
			}
		}
		JOBS = _jobs;
	}
	~GA() {}

	Individual run(int maxGeneration, int populationSize, int offspringAmount, int elitism) {
		std::vector<Individual> population;
		Individual best(&REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
		for (size_t i = 0; i < populationSize; i++) {
			Individual individual(population, &REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
			individual.evaluate();
			if (individual < best) {
				best = individual;
			}
			population.push_back(individual);
		}
		float p = 1 / (REQUIRED_OPERATIONS.size() + AVAILABLE_WORKSTATIONS.size());
		std::sort(population.begin(), population.end());
		std::vector<Individual> offsprings;
		_tournamentSize = population.size() / 10;
		std::vector<Individual> selectionPool;
		for (size_t i = 0; i < maxGeneration; i++) {
			if (i % 100 == 0) {
				std::cout << "Generation: " << i << ", Current Best: " << best.getFitness() << ", Generation Best: " << population[0].getFitness() << ", Generation Average: " << averageFitness(population) << std::endl;
			}
			offsprings.clear();
			for (size_t j = 0; j < offspringAmount; j+=2) {
				Individual offspringA;
				Individual offspringB;
				recombine(population, &offspringA, &offspringB);
				offspringA.mutate(p);
				while (std::count(offsprings.begin(), offsprings.end(), offspringA) > 1) {
					Individual replacement(offsprings, &REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
					replacement.evaluate();
					offspringA = replacement;
				}
				offspringA.evaluate();
				offsprings.push_back(offspringA);
				if (offsprings.size() < offspringAmount) {
					offspringB.mutate(p);
					while (std::count(offsprings.begin(), offsprings.end(), offspringB) > 1) {
						Individual replacement(offsprings, &REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
						replacement.evaluate();
						offspringB = replacement;
					}
					offspringB.evaluate();
					offsprings.push_back(offspringB);
				}
			}
			selectionPool.clear();
			selectionPool.insert(selectionPool.begin(), offsprings.begin(), offsprings.end());
			if (elitism > 0) {
				selectionPool.insert(selectionPool.end(), population.begin(), population.begin() + elitism);
			}
			for (size_t j = 0; j < populationSize; j++) {
				while (std::count(selectionPool.begin(), selectionPool.end(), selectionPool[j]) > 1) {
					Individual replacement(selectionPool, &REQUIRED_OPERATIONS, &AVAILABLE_WORKSTATIONS, &AVAILABLE_WORKERS, &BASE_DURATIONS, &JOBS);
					replacement.evaluate();
					selectionPool[j] = replacement;
				}
			}
			std::sort(selectionPool.begin(), selectionPool.end());
			population.clear();
			population.insert(population.end(), selectionPool.begin(), selectionPool.begin() + populationSize);
			if (population[0] < best) {
				best = population[0];
			}
		}
		return best;
	}
};

