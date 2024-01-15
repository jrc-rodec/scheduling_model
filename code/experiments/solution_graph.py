class Operation:

    def __init__(self, sequence_index, machine, job, assignment):
        self.sequence = sequence_index
        self.assignment = assignment
        self.job = job
        self.machine = machine
        self.children : list[Operation] = [] # technically there should also be max. 2 children (machine child, job child)
        # make a connection in both directions for faster tree search
        self.machine_parent = None
        self.sequence_parent = None

    def __eq__(self, other):
        return self.job == other.job and self.sequence == other.sequence
    
    def __ne__(self, other):
        return not self == other

class SolutionGraph:

    def __init__(self):
        self.roots : list[Operation] = []
    
    def add_root(self, operation : Operation):
        self.roots.append(operation)

    def add_root(self, job, assignment, machine, operation_index = 0):
        self.roots.append(Operation(operation_index, machine, job, assignment))

    def insert(self, job, assignment, operation_index, machine, traversal : str = 'bf'):
        operation = Operation(operation_index, machine, job, assignment)
        closed_list : list[Operation] = []
        machine_parent = None
        sequence_parent = None
        for root in self.roots:
            # traverse root
            open_list : list[Operation] = []
            open_list.extend(root.children)
            while len(open_list) > 0 and not (machine_parent and sequence_parent):
                current = open_list.pop(0)
                # compare for machine parent
                if operation.assignment == current.assignment and operation.machine -1 == current.machine:
                    machine_parent = current
                    if sequence_parent:
                        break
                # compare for sequence parent
                if operation.job == current.job and operation.sequence -1 == current.sequence:
                    sequence_parent = current
                    if machine_parent:
                        break
                closed_list.append(current)
                for child in current.children:
                    if child not in open_list and child not in closed_list:
                        if traversal == 'bf':
                            open_list.append(child)
                        else: #df
                            open_list.insert(0, child)
            if machine_parent and sequence_parent:
                break
        if machine_parent or sequence_parent:
            if machine_parent:
                machine_parent.children.append(operation)
                operation.machine_parent = machine_parent
            if sequence_parent:
                sequence_parent.children.append(operation)
                operation.sequence_parent = sequence_parent
        else:
            self.add_root(operation)

    def max_depth(self):
        pass

    def find(self, job, operation, traversal = 'bf') -> Operation:
        closed_list : list[Operation] = []
        for root in self.roots:
            # traverse root
            open_list : list[Operation] = []
            open_list.extend(root.children)
            while len(open_list) > 0:
                current = open_list.pop(0)
                
                if current.job == job and current.sequence == operation:
                    return current

                closed_list.append(current)
                for child in current.children:
                    if child not in open_list and child not in closed_list:
                        if traversal == 'bf':
                            open_list.append(child)
                        else: #df
                            open_list.insert(0, child)
        return None

    def are_dependent(self, job_a, operation_a, job_b, operation_b, traversal='bf'):
        if job_a == job_b:
            return True
        o_a = self.find(job_a, operation_a, traversal)
        # search children
        open_list = []
        closed_list = []
        open_list.extend(o_a.children)
        while len(open_list) > 0:
            current = open_list.pop(0)
            if current.job == job_b and current.sequence == operation_b:
                return True
            closed_list.append(current)
            for child in current.children:
                if child not in open_list and child not in closed_list:
                    if traversal == 'bf':
                        open_list.append(child)
                    else: #df
                        open_list.insert(0, child)
        # search in parent direction
        open_list = []
        closed_list = []
        if self.machine_parent:
            open_list.append(self.machine_parent)
        if self.sequence_parent:
            open_list.append(self.sequence_parent)
        while len(open_list) > 0:
            current = open_list.pop(0)
            if current.job == job_b and current.sequence == operation_b:
                return True
            closed_list.append(current)
            if current.machine_parent and current.machine_parent not in open_list and current.machine_parent not in closed_list:
                open_list.append(current.machine_parent)
            if current.sequence_parent and current.sequence_parent not in open_list and current.sequence_parent not in closed_list:
                open_list.append(current.sequence_parent)
        return False

    def get_dependency(self, job_a, operation_a, job_b, operation_b):
        pass

    def get_depth(self, job, operation):
        pass

    def get_depth(self, assignment, machine_index):
        pass

    def get_assignment(self, job, operation):
        pass

    def get_job(self, assignment, machine_index):
        pass

    def create(self, sequence, assignments):
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
