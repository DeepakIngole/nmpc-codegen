import sys
sys.path.insert(0, './src_python')
import nmpccodegen as nmpc
import nmpccodegen.tools as tools
import nmpccodegen.models as models
import nmpccodegen.controller as controller
import nmpccodegen.Cfunctions as cfunctions

import math
import ctypes
import numpy as np
import matplotlib.pyplot as plt

import math
import sys
import time

controller_name="toturial_controller"

## -- GENERATE STATIC FILES --
# start by generating the static files and folder of the controller
location_nmpc_repo = "."
output_locationcontroller = location_nmpc_repo + "/test_controller_builds"
trailer_controller_location = output_locationcontroller + "/" + controller_name + "/"

tools.Bootstrapper.bootstrap(output_locationcontroller, controller_name, python_interface_enabled=True)
## -----------------------------------------------------------------

# get the continuous system equations from the existing library
(system_equations, number_of_states, number_of_inputs, coordinates_indices) = nmpc.example_models.get_trailer_model(
    L=0.5)

step_size = 0.05
simulation_time = 10
number_of_steps = math.ceil(simulation_time / step_size)
horizon = 10

integrator = "RK44" # select a Runga-Kutta  integrator (FE is forward euler)
constraint_input = cfunctions.IndicatorBoxFunction([-1, -1], [1, 1])  # input needs stay within these borders
model = models.Model_continious(system_equations, constraint_input, step_size, number_of_states, \
                                number_of_inputs, coordinates_indices, integrator)

# Q and R matrixes determined by the control engineer.
Q = np.diag([10., 10000., 1.])
R = np.eye(model.number_of_inputs, model.number_of_inputs) * 1.

# the stage cost is defined two lines,different kinds of stage costs are available to the user.
stage_cost = controller.Stage_cost_QR(model, Q, R)

# define the controller
trailer_controller = controller.Nmpc_panoc(trailer_controller_location, model, stage_cost)
trailer_controller.horizon = horizon # NMPC parameter
trailer_controller.integrator_casadi = True # optional  feature that can generate the integrating used  in the cost function
trailer_controller.panoc_max_steps = 10000 # the maximum amount of iterations the PANOC algorithm is allowed to do.
trailer_controller.min_residual=-10
trailer_controller.shooting_mode="multiple shot"

# add an obstacle, a two dimensional rectangle
# obstacle_weight = 1000.
x_up = 1.
x_down = 0.5
y_up = 0.4
y_down = 0.2
obstacle = controller.Basic_obstacles.generate_rec_object(x_up, x_down, y_up, y_down)
# trailer_controller.add_obstacle(obstacle)

# generate the dynamic code
trailer_controller.generate_code()

# -- simulate controller --
# sim.set_weight_obstacle(0,1000.)

initial_state = np.array([0.01, 0., 0.])
# initial states of the multiple shoot should be a good guess of the traject
initial_states_matrix=np.zeros((number_of_states,horizon-1))
for i in range(0,horizon-1):
    initial_states_matrix[0,i] = 2*(i/(horizon-1))+0.01
    initial_states_matrix[1,i] = 0.5*(i/(horizon-1))
    initial_states_matrix[2, i] = 0

initial_states=np.reshape(initial_states_matrix.T,(number_of_states*(horizon-1),1))

reference_state = np.array([2, 0.5, 0])
reference_input = np.array([0, 0])

# setup a simulator to test
sim = tools.Simulator(trailer_controller.location)

# init the controller
sim.simulator_init()

j=number_of_inputs*horizon
for i in range(0,number_of_states*(horizon-1)):
    sim.set_init_value_solver(initial_states[i],j)
    j+=1

# simulate and get the whole horizon of inputs
(sim_data,full_solution,extra_values)= sim.simulate_nmpc_multistep_solution(initial_state,reference_state,reference_input,horizon,(horizon-1)*number_of_states)
print("solved problem in "+str(sim_data.panoc_interations)+" iterations")

# cleanup the controller
sim.simulator_cleanup()

# calculate the states using these inputs
state = initial_state
state_history = np.zeros((number_of_states, horizon))
for i in range(0,horizon):
    state = model.get_next_state_numpy(state,full_solution[:,i])
    state_history[:,i]=np.ravel(state)

print("Final state:")
print(state)

# get the intermediate states
inter_states = np.reshape(extra_values.T,(number_of_states,horizon-1))

plt.figure(1)
plt.subplot(211)
# plt.plot(initial_states_matrix[0, :], initial_states_matrix[1, :])
plt.plot(state_history[0, :], state_history[1, :])
plt.subplot(212)
plt.plot(state_history[2, :])
plt.savefig(controller_name + '.png')
plt.figure(2)
plt.plot(inter_states[0,:],inter_states[1,:])
plt.show()