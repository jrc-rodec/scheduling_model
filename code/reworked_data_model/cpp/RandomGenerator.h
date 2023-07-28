#pragma once
#include <random>
class RandomGenerator {
public:

	std::mt19937 rng;

	RandomGenerator() {
		std::random_device dev;
		rng = std::mt19937(dev());
	}

	double randomDouble() {
		// return value between 0 and 1 -> 1 not included apparently
		std::uniform_real_distribution<> distribution(0.0, 1.0);
		return distribution(rng);
		//return ((double)std::rand() / (RAND_MAX));
	}
	int randomInteger(int low, int high) {
		// NOTE: lower bound and upper bound are included
		std::uniform_int_distribution<uint32_t> distribution(low, high);
		return distribution(rng);
	}
};

