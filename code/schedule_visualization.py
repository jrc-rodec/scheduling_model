import matplotlib.pyplot as plt
import matplotlib
from matplotlib import pylab
def draw_schedule(self):

   
        # set size of schedule (in inches), minimal height/width required to see all labels
        minimum_schedule_width = 6
        minimum_schedule_height = 3.5

        schedule_width = minimum_schedule_width
        schedule_height = minimum_schedule_height

        # initialize plot & set basic elements
        fig = pylab.figure(figsize=[schedule_width, schedule_height], dpi=80) # 80 dots per inch
        ax = fig.gca()

        colors = matplotlib.cm.Dark2.colors
        broken_workstation_color = 'tab:red'

        products_in_schedule = []
        workstations_in_schedule = []
        affected_products = [] # mark products which are affected from broken workstation
        broken_workstations_in_schedule = []

        # get names of products and workstations in schedule
        for step in self.schedule: 
            if not (step.Product.name in products_in_schedule):
                products_in_schedule.append(step.Product.name)
            if not (step.Workstation.name in workstations_in_schedule):
                workstations_in_schedule.append(step.Workstation.name)

        products_in_schedule.sort()
        workstations_in_schedule.sort() # needed so that the workstations are alphabetically sorted in labels


        # draw schedule
        for step in self.schedule:
            name_of_product = step.Product.name
            index_of_product = products_in_schedule.index(name_of_product)
            index_of_workstation = workstations_in_schedule.index(step.Workstation.name)
            duration = step.End_Time - step.Start_Time

            # mark all products in affected workstation as broken and also all future steps of affected products
            if (step.Workstation.name in broken_workstations_in_schedule and step.End_Time > self.time) or (name_of_product in affected_products and step.End_Time > self.time):
                ax.broken_barh([(step.Start_Time, duration)], (index_of_workstation + 0.5, 0.9), facecolors=broken_workstation_color, alpha=1, hatch='x')
                if name_of_product not in affected_products: 
                    affected_products.append(name_of_product)
            else:
                ax.broken_barh([(step.Start_Time, duration)], (index_of_workstation + 0.5, 0.9), facecolors=colors[index_of_product % len(2)], alpha=1) # draw one bar of plot (= step in schedule)
                if name_of_product in affected_products: 
                    affected_products.remove(name_of_product)
            
            # add product name to center of bar
            ax.text((step.Start_Time + step.End_Time)/2, index_of_workstation + 0.9, name_of_product, {'ha':'center', 'va':'center', 'weight':'bold'})

        # set axis ticks, labels and grid
        ax.set_title("Schedule")
        ax.set_xlabel("Time",)
        ax.set_ylabel("Workstation")

        ax.set_yticks(range(1, 1+len(workstations_in_schedule)), labels=workstations_in_schedule) # set workstation names as ticks on y axis

        ax.grid(True, linewidth=0.1)
        matplotlib.pyplot.rcParams['hatch.linewidth'] = 0.2 # lower line width of hatch

        # set label & grid line of corresponding workstations to inactive color
        for workstation in broken_workstations_in_schedule:
            if workstation in workstations_in_schedule:
                index_of_broken_workstation = workstations_in_schedule.index(workstation)
                gridline = ax.get_ygridlines()[index_of_broken_workstation]
                gridline.set_color(broken_workstation_color)
                gridline.set_linewidth(1)
                ax.get_yticklabels()[index_of_broken_workstation].set_color(broken_workstation_color)

        # show where we are at the time line right now
        ax.axvline(self.time, color='gray')

        # remove margins around plot
        fig.tight_layout()

        fig.show()

        matplotlib.pyplot.close()