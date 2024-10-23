import pyswarms as ps

def rosenbrock_with_args(x, a, b, c=0):
    f = (a - x[:, 0]) ** 2 + b * (x[:, 1] - x[:, 0] ** 2) ** 2 + c
    return f


# Set-up hyperparameters
options = {'c1': 0.5, 'c2': 0.3, 'w':0.9}

n_operations = 50
x_max = [1.0] * n_operations
x_min = [0.0] * n_operations
bounds = (x_min, x_max)

# Call instance of PSO with bounds argument
optimizer = ps.single.GlobalBestPSO(n_particles=10, dimensions=2, options=options, bounds=bounds)

kwargs={"a": 1.0, "b": 100.0, 'c':0}
# Perform optimization
cost, pos = optimizer.optimize(rosenbrock_with_args, iters=1000, **kwargs)



def fitness_function(x):
    sum = 0
    for i in range(len(x)):
        sum += x[i]
    return sum

x0 = 8 * [0]
xopt, es = cma.fmin2(fitness_function, x0 , 0.5, {'integer_variables': list(range(len(x0))), 'bounds': [0, 100]})#'bounds': [-1, 15 - 1e-9]})#, {'verb_disp': 1})
int_result = [np.floor(x) for x in es.result[0]] #NOTE: the cma library truncates/rounds all values in the background itself, apparently np.floor
print(f'Result: {int_result}')

print(xopt)