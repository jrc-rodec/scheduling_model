class Operation:

    def __init__(self, operation_index, machine, job, assignment, machine_parent = None, job_parent = None, machine_child = None, job_child = None, start_time = 0, end_time = 0):
        self.operation = operation_index
        self.assignment = assignment
        self.job = job
        self.machine = machine
        self.machine_child = machine_child
        self.job_child = job_child
        # make a connection in both directions for faster tree search
        self.machine_parent = machine_parent
        self.job_parent = job_parent
        self.start_time = start_time
        self.end_time = end_time
        
    def is_leaf(self):
        return not (self.machine_child or self.job_child)
    
    def is_root(self):
        return not (self.machine_parent or self.job_parent)
    
    def is_first_on_machine(self):
        return not self.machine_parent
    
    def is_first_operation(self):
        return not self.job_parent

    def __eq__(self, other):
        return self.job == other.job and self.operation == other.sequence
    
    def __ne__(self, other):
        return not self == other

class SolutionGraph:

    def __init__(self, sequence, assignments, duration_matrix : list[int, int], traverse_mode = 'bf', lazy = True):
        self.roots : list[Operation] = []
        self.traverse_mode = traverse_mode
        self.durations = duration_matrix
        self.sequence = sequence
        self.assignments = assignments
        self.job_indices = []
        self._create(sequence, assignments)
        self.makespan = 0 if lazy else self.determine_makespan()
        self.lazy = lazy
    
    def _add_root(self, operation : Operation):
        self.roots.append(operation)

    def _add_root(self, job, assignment, machine, operation_index = 0):
        self.roots.append(Operation(operation_index, machine, job, assignment))

    def _add_children(self, operation, open_list, closed_list = []):
        if operation.machine_child and operation.machine_child not in open_list and operation.machine_child not in closed_list:
            if self.traverse_mode == 'bf':
                open_list.append(operation.machine_child)
            else:
                open_list.insert(0, operation.machine_child)
        if operation.job_child and operation.job_child not in open_list and operation.job_child not in closed_list:
            if self.traverse_mode == 'bf':
                open_list.append(operation.job_child)
            else:
                open_list.insert(0, operation.job_child)

    def _get_duration(self, operation):
        return self.durations[operation.assignment][self.job_indices[operation.job] + operation.operation]

    def insert(self, job, assignment, operation_index, machine):
        operation = Operation(operation_index, machine, job, assignment)
        closed_list : list[Operation] = []
        machine_parent = None
        sequence_parent = None
        for root in self.roots:
            open_list : list[Operation] = []
            self._add_children(root, open_list, closed_list)
            while len(open_list) > 0 and not (machine_parent and sequence_parent):
                current = open_list.pop(0)
                # compare for machine parent
                if operation.assignment == current.assignment and operation.machine -1 == current.machine:
                    machine_parent = current
                    if sequence_parent:
                        break
                # compare for sequence parent
                if operation.job == current.job and operation.operation -1 == current.operation:
                    sequence_parent = current
                    if machine_parent:
                        break
                closed_list.append(current)
                self._add_children(current, open_list, closed_list)
            if machine_parent and sequence_parent:
                break
        if machine_parent or sequence_parent:
            if machine_parent:
                machine_parent.machine_child = operation
                operation.machine_parent = machine_parent
                operation.start_time = machine_parent.end_time
                operation.end_time = operation.start_time + self._get_duration(operation)
            if sequence_parent:
                sequence_parent.job_child = operation
                operation.job_parent = sequence_parent
                if operation.start_time < sequence_parent.end_time:
                    operation.start_time = sequence_parent.end_time
                    operation.end_time = operation.start_time + self._get_duration(operation)
        else:
            self._add_root(operation)
        if not self.lazy:
            self.determine_makespan()

    def max_depth(self):
        pass

    def find_operation(self, job, operation) -> Operation:
        closed_list : list[Operation] = []
        for root in self.roots:
            open_list : list[Operation] = []
            self._add_children(root, open_list, closed_list)
            while len(open_list) > 0:
                current = open_list.pop(0)
                
                if current.job == job and current.operation == operation:
                    return current

                closed_list.append(current)
                self._add_children(current, open_list, closed_list)
        return None
    
    def find_machine(self, assignment, machine_index) -> Operation:
        closed_list : list[Operation] = []
        for root in self.roots:
            open_list : list[Operation] = []
            self._add_children(root, open_list, closed_list)
            while len(open_list) > 0:
                current = open_list.pop(0)
                
                if current.assignment == assignment and current.machine == machine_index:
                    return current

                closed_list.append(current)
                self._add_children(current, open_list, closed_list)
        return None
    
    def _is_predecessor(self, operation_a, operation_b):
        # NOTE: if they are equal, False
        if operation_a == operation_b:
            return False
        closed_list = []
        open_list = []
        self._add_children(operation_a, open_list, closed_list)
        while len(open_list) > 0:
            current = open_list.pop(0)
            if current.job == operation_b.job and current.operation == operation_b.operation:
                return True
            closed_list.append(current)
            self._add_children(current, open_list, closed_list)
        return False

    def _is_successor(self, operation_a, operation_b):
        return self._is_predecessor(operation_b, operation_a)

    def are_dependent(self, job_a, operation_a, job_b, operation_b):
        if job_a == job_b:
            return True
        o_a = self.find_operation(job_a, operation_a)
        o_b = self.find_operation(job_b, operation_b)
        return self._is_predecessor(o_a, o_b) or self._is_successor(o_a, o_b)

    def get_dependency(self, job_a, operation_a, job_b, operation_b):
        pass

    def get_depth(self, job, operation):
        pass

    def get_depth(self, assignment, machine_index):
        pass

    def get_assignment(self, job, operation):
        operation = self.find_operation(job, operation)
        if operation:
            return operation.assignment
        return None

    def get_job(self, assignment, machine_index):
        operation = self.find_machine(assignment, machine_index)
        if operation:
            return operation.job
        return None

    def _create(self, sequence, assignments):
        machines = [ x for i, x in enumerate(assignments) if x not in assignments[:i]]
        jobs = [ x for i, x in enumerate(sequence) if x not in sequence[:i]]
        machine_indices = [0] * len(machines)
        operation_indices = [0] * len(jobs)
        # get start indices for each job
        job_indices = [0] * len(jobs)
        for i in range(len(jobs)):
            if i > 0:
                n_ops = 0
                for j in range(sequence):
                    if sequence[j] == i-1:
                        n_ops += 1
                job_indices[i] = job_indices[i-1] + n_ops
        for i in range(len(sequence)): # NOTE: sequence and assignments should have the same length
            job = sequence[i]
            operation_index = operation_indices[job]
            
            machine = assignments[job_indices[job] + operation_index]
            machine_index = machine_indices[machine]
            
            self.insert(job, machine, operation_index, machine_index)

            machine_indices[machine] += 1
            operation_indices[job] += 1
        self.job_indices = job_indices

    def determine_makespan(self):
        makespan = 0
        closed_list = []
        for root in self.roots:
            open_list = []
            self._add_children(root, open_list, closed_list)
            while len(open_list) > 0:
                current = open_list.pop(0)
                #probably not more efficient than just comparing times
                if current.is_leaf():
                    if current.end_time > makespan:
                        makespan = current.end_time
                closed_list.append(current)
                self._add_children(current, open_list, closed_list)
        return makespan
