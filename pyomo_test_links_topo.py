import polars as pl
import math
import pyomo.environ as pyo
import plotly.graph_objects as go

# Read data from CSV using polars
data = pl.read_csv("nodes.csv")
links = pl.read_csv("links.csv")

# Extract data into dictionaries
coordinates = {row['cell_id']: (row['x_coord'], row['y_coord']) for row in data.to_dicts()}
population = {row['cell_id']: row['population'] for row in data.to_dicts()}

#Given network topology
allowed_links = links.rows() + [(pair[1], pair[0]) for pair in links.rows()]
#print(allowed_links)

demand_per_person_per_day = 2  # m3/day
max_supply_terminal_capacity = 22000000  # m3/day

# Calculate demand per node
demand = {i: population[i] * demand_per_person_per_day for i in population}

# Calculate distances between cells
def euclidean_distance(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

distances = {(i, j): euclidean_distance(coordinates[i], coordinates[j]) for i, j in allowed_links}

# Capital and operating costs
capital_cost_per_km = 1e6  # £1m per km
operating_cost_per_1000_m3_km = 0.15  # £0.15 per 1000 m3 km

# Define the Pyomo model
model = pyo.ConcreteModel()

# Sets
model.i = pyo.Set(initialize=coordinates.keys())
model.link = pyo.Set(initialize=allowed_links, dimen=2)

# Parameters
model.d = pyo.Param(model.i, initialize=demand)
model.dist = pyo.Param(model.link, initialize=distances, default=0)

# Variables
model.x = pyo.Var(model.link, within=pyo.Binary)
model.f = pyo.Var(model.link, within=pyo.NonNegativeReals)

# Objective function
capital_cost = sum(capital_cost_per_km * model.dist[i, j] * model.x[i, j] for i, j in model.link)
#operating_cost = sum(operating_cost_per_1000_m3_km * model.dist[i, j] * model.f[i, j] / 1000 for i, j in model.link)

#switch here
model.objective = pyo.Objective(rule=capital_cost, sense=pyo.minimize)

# Constraints
def flow_balance_rule(model, i):
    if i == 1:
        return sum(model.f[i, j] for j in model.i if (i, j) in model.link) == sum(model.d[j] for j in model.i if j != 1)
    else:
        return sum(model.f[j, i] for j in model.i if (j, i) in model.link) - sum(model.f[i, j] for j in model.i if (i, j) in model.link) == model.d[i]

model.flow_balance = pyo.Constraint(model.i, rule=flow_balance_rule)

# # Big-M constraints
M = 1e10  # Large constant
epsilon = 1e-4  # Small positive number

def big_M_upper_bound_rule(model, i, j):
    return model.f[i, j] <= M * model.x[i, j]

def big_M_non_zero_rule(model, i, j):
    return model.f[i, j] >= epsilon * model.x[i, j]

model.big_M_upper_bound = pyo.Constraint(model.link, rule=big_M_upper_bound_rule)
model.big_M_non_zero = pyo.Constraint(model.link, rule=big_M_non_zero_rule)

# Bi-directional Links Constraints
def bidirectionl_link_rule(model, i, j):
    for (i, j) in model.link:
        return model.x[i, j] + model.x[j, i] == 1
model.links_rule = pyo.Constraint(model.link, rule = bidirectionl_link_rule)

# Solve the model
solver = pyo.SolverFactory('cbc')# executeble = cbc_path, not pickup the path. for venv, cbc.exe is downloaded manaully and put in venv/Scripts
result = solver.solve(model, tee=True)

# Print the results
if result.solver.status == pyo.SolverStatus.ok and result.solver.termination_condition == pyo.TerminationCondition.optimal:
    print(f"Total Cost: {pyo.value(model.objective)}")

    # Extracting the results
    pipelines = [(i, j) for (i,j) in model.link if pyo.value(model.x[i, j]) != 0]
    flows = {(i, j): pyo.value(model.f[i, j]) for (i,j) in model.link if pyo.value(model.x[i,j]) != 0}

    # Visualization using Plotly
    fig = go.Figure()

    # Add pipelines
    for (i, j) in pipelines:
        print(pyo.value(model.f[i, j]))
        fig.add_trace(go.Scatter(x=[coordinates[i][0], coordinates[j][0]], 
                                 y=[coordinates[i][1], coordinates[j][1]], 
                                 mode='lines', 
                                 line=dict(width=2, color='red'),
                                 name=f'Pipeline {i}-{j}'))
    # Add cell points
    for i in coordinates:
        fig.add_trace(go.Scatter(x=[coordinates[i][0]], 
                                 y=[coordinates[i][1]], 
                                 mode='markers+text', 
                                 marker=dict(size=6, color='green'),
                                 text=[f'Node {i}'],
                                 textposition="top center"))

    fig.update_layout(title='Gas Distribution Network',
                      xaxis_title='X Coordinate (km)',
                      yaxis_title='Y Coordinate (km)',
                      showlegend=True)

    fig.show()
else:
    print("No feasible solution found")
    print("Solver Status:", result.solver.status)
    print("Termination Condition:", result.solver.termination_condition)

#model.display()

# check for constraint violations
print("\nchecking constraint violations:")
for i in model.i:
    inflow = sum(pyo.value(model.f[j, i]) for j in model.i if (j, i) in model.link)
    outflow = sum(pyo.value(model.f[i, j]) for j in model.i if (i, j) in model.link)
    demand = pyo.value(model.d[i])
    print(f"node {i}: inflow = {inflow}, outflow = {outflow}, demand = {demand}")
    print(f"check if flow balanced: {bool(abs(demand - (inflow - outflow))<=0.001)}, and the error is {demand - (inflow - outflow)}")

# check the values of decision variables
print("\ndecision variable values:")
for (i, j) in model.link:
    print(f"flow from node {i} to node {j}: {pyo.value(model.f[i, j])}")
    print(f"pipeline from node {i} to node {j}: {pyo.value(model.x[i, j])}")