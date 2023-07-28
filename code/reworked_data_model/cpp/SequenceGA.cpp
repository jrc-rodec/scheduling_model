// SequenceGA.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include "ga.h"
float runWithTestData() {
    // expected result: 20
    std::vector<int> jobs = { 0, 0, 1, 1, 2, 2, 3 };
    std::vector<std::vector<int>> availableWorkstations = {
        {0, 1},
        {1, 2},
        {0, 2},
        {2, 3},
        {0, 3},
        {1, 3},
        {1, 2}
    };
    std::vector<std::vector<int>> durations = { // best workstations: 0, 1, 2, 2, 1, 3, 2 
        {5, 10, 0, 0},
        {0, 10, 15, 0},
        {10, 0, 5, 0},
        {0, 0, 5, 10},
        {10, 0, 0, 5},
        {0, 15, 0, 20},
        {0, 20, 5, 0}
    };
    GA ga(jobs, availableWorkstations, durations);
    Individual result = ga.run(1000, 50, 100, 5);
    return result.getFitness();
}

float runFattahi1() {
    // expected result: 66
    std::vector<int> jobs = { 0, 0, 1, 1 };
    std::vector<std::vector<int>> availableWorkstations = {
        {0, 1},
        {0, 1},
        {0, 1},
        {0, 1}
    };
    std::vector<std::vector<int>> durations = {
        {25, 37},
        {32, 24},
        {45, 65},
        {21, 65},
    };

    GA ga(jobs, availableWorkstations, durations);
    Individual result = ga.run(1000, 50, 100, 5);
    return result.getFitness();
}

float runFattahi10() {
    // expected result: 516?
    std::vector<int> jobs = { 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3 };
    // [[0], [1, 3], [3, 4], [0, 2], [1, 2], [4], [0, 1], [2], [3, 4], [0, 1], [4], [2, 3]]
    std::vector<std::vector<int>> availableWorkstations = {
        {0},
        {1, 3},
        {3, 4},
        {0, 2},
        {1, 2},
        {4},
        {0, 1},
        {2},
        {3, 4},
        {0, 1},
        {4},
        {2, 3}
    };
    //[[147, 0, 0, 0, 0], [0, 130, 0, 140, 0], [0, 0, 0, 150, 160], [214, 0, 150, 0, 0], [0, 66, 87, 0, 0], [0, 0, 0, 0, 178], [87, 62, 0, 0, 0], [0, 0, 180, 0, 0], [0, 0, 0, 190, 100], [87, 65, 0, 0, 0], [0, 0, 0, 0, 173], [0, 0, 136, 145, 0]]
    std::vector<std::vector<int>> durations = {
        {147, 0, 0, 0, 0},
        {0, 130, 0, 140, 0},
        {0, 0, 0, 150, 160},
        {214, 0, 150, 0, 0},
        {0, 66, 87, 0, 0},
        {0, 0, 0, 0, 178},
        {87, 62, 0, 0, 0},
        {0, 0, 180, 0, 0},
        {0, 0, 0, 190, 100},
        {87, 65, 0, 0, 0},
        {0, 0, 0, 0, 173},
        {0, 0, 136, 145, 0}
    };

    GA ga(jobs, availableWorkstations, durations);
    Individual result = ga.run(1000, 50, 100, 5);
    return result.getFitness();
}

float runFattahi20() {
    // expected result < 1276
    std::vector<int> jobs = { 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11 };
    std::vector<std::vector<int>> availableWorkstations = {
        {0, 1, 2}, {1, 3, 6}, {3, 4, 6}, {6, 7}, {0, 2}, {1, 2}, {4, 5, 6}, {4, 7}, {0, 1}, {2, 3, 6}, {3, 4, 5}, {5, 7}, {0, 1}, {2, 4}, {3, 5}, {4, 5}, {0, 1, 2}, {3, 4, 6}, {1, 4, 5}, {5, 7}, {1, 2, 3}, {2, 3, 4}, {4, 5, 6}, {3, 6}, {1, 2}, {2, 4}, {4, 5,
6}, {4, 7}, {2, 3}, {4, 5}, {4, 5, 6}, {6, 7}, {1, 2}, {2, 3}, {4, 6}, {5, 7}, {2, 3}, {4, 5}, {4, 5, 6}, {6, 7}, {1, 2}, {2, 3}, {4, 6}, {5, 7}, {1, 2}, {2, 4}, {4, 5, 6}, {4, 7}
    
    };
    std::vector<std::vector<int>> durations = {
{247, 223, 100, 0, 0, 0, 0, 0}, {0, 130, 0, 140, 0, 0, 123, 0}, {0, 0, 0, 150, 160, 0, 200, 0}, {0, 0, 0, 0, 0, 0, 210, 145}, {214, 0, 150, 0, 0, 0, 0, 0}, {0, 66, 87, 0, 0, 0, 0, 0},
     {0, 0, 0, 0, 178, 95, 150, 0}, {0, 0, 0, 0, 120, 0, 0, 150}, {87, 62, 0, 0, 0, 0, 0, 0}, {0, 0, 180, 105, 0, 0, 145, 0}, {0, 0, 0, 190, 100, 153, 0, 0}, {0, 0, 0, 0, 0, 170, 0, 165},
     {87, 65, 0, 0, 0, 0, 0, 0}, {0, 0, 250, 0, 173, 0, 0, 0}, {0, 0, 0, 145, 0, 136, 0, 0}, {0, 0, 0, 0, 250, 170, 0, 0}, {128, 123, 145, 0, 0, 0, 0, 0}, {0, 0, 0, 65, 47, 0, 86, 0},
     {0, 100, 0, 0, 110, 85, 0, 0}, {0, 0, 0, 0, 0, 180, 0, 165}, {0, 145, 320, 154, 0, 0, 0, 0}, {0, 0, 123, 150, 192, 0, 0, 0}, {0, 0, 0, 0, 120, 240, 180, 0}, {0, 0, 0, 120, 0, 0, 50, 0},
     {0, 157, 145, 0, 0, 0, 0, 0}, {0, 0, 124, 0, 168, 0, 0, 0}, {0, 0, 0, 0, 145, 165, 178, 0}, {0, 0, 0, 0, 140, 0, 0, 230}, {0, 0, 257, 245, 0, 0, 0, 0}, {0, 0, 0, 0, 268, 224, 0, 0},
     {0, 0, 0, 0, 145, 165, 178, 0}, {0, 0, 0, 0, 0, 0, 150, 150}, {0, 150, 150, 0, 0, 0, 0, 0}, {0, 0, 180, 220, 0, 0, 0, 0}, {0, 0, 0, 0, 40, 0, 50, 0}, {0, 0, 0, 0, 0, 150, 0, 170},
     {0, 0, 257, 245, 0, 0, 0, 0}, {0, 0, 0, 0, 268, 224, 0, 0}, {0, 0, 0, 0, 145, 165, 178, 0}, {0, 0, 0, 0, 0, 0, 150, 150}, {0, 150, 150, 0, 0, 0, 0, 0}, {0, 0, 180, 220, 0, 0, 0, 0},
     {0, 0, 0, 0, 40, 0, 50, 0}, {0, 0, 0, 0, 0, 150, 0, 170}, {0, 357, 345, 0, 0, 0, 0, 0}, {0, 0, 224, 0, 268, 0, 0, 0}, {0, 0, 0, 0, 145, 165, 178, 0}, {0, 0, 0, 0, 340, 0, 0, 230}
    };

    GA ga(jobs, availableWorkstations, durations);
    Individual result = ga.run(10000, 300, 600, 30);
    return result.getFitness();
}

int main()
{
    std::srand(static_cast<unsigned int>(std::time(nullptr)));

    std::cout << runFattahi20() << std::endl;
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
