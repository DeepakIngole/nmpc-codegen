import casadi as cd
from .casadi_code_generator import Casadi_code_generator as ccg
       
class Multiple_shot_definition:
    """ multiple shot nmpc defintion """
    def __init__(self,controller):
        self._controller=controller
        self._dimension=controller.model.number_of_inputs * controller.horizon + controller.model.number_of_states*(controller.horizon-1)
    def generate_cost_function(self):
        initial_state = cd.SX.sym('initial_state', self._controller.model.number_of_states, 1)
        state_reference = cd.SX.sym('state_reference', self._controller.model.number_of_states, 1)
        input_reference = cd.SX.sym('input_reference', self._controller.model.number_of_inputs, 1)
        obstacle_weights = cd.SX.sym('obstacle_weights', self._controller.number_of_obstacles, 1)

        input_all_steps = cd.SX.sym('input_all_steps', self._controller.model.number_of_inputs * self._controller.horizon + \
                                    self._controller.model.number_of_states * (self._controller.horizon-1), 1)
        cost = cd.SX.sym('cost', 1, 1)
        cost = 0

        current_init_state = initial_state
        for i in range(1, self._controller.horizon + 1):
            current_input = input_all_steps[(i - 1) * self._controller.model.number_of_inputs:i * self._controller.model.number_of_inputs]

            next_state_bar = self._controller.model.get_next_state(current_init_state,current_input)

            cost = cost + self._controller.stage_cost(next_state_bar, current_input, i, state_reference, input_reference)
            cost = cost + self._controller.generate_cost_obstacles(next_state_bar, obstacle_weights)

            # add a soft constraint for the continuity
            weight_continuity = 0
            if i > 1 :
                cost = cost + \
                       weight_continuity*(\
                           cd.sum1(\
                                (previous_next_state_bar-current_init_state)**2\
                            )\
                        )

            previous_next_state_bar = next_state_bar
            if i<self._controller.horizon: # don't do this is this is the last loop
                offset_inputs = self._controller.model.number_of_inputs * self._controller.horizon
                current_init_state = input_all_steps[offset_inputs+(i-1)*self._controller.model.number_of_states: \
                    offset_inputs + i * self._controller.model.number_of_states]

        (cost_function, cost_function_derivative_combined) = \
            ccg.setup_casadi_functions_and_generate_c(initial_state, input_all_steps, \
                                                      state_reference, input_reference, obstacle_weights, cost, \
                                                      self._controller.location)
        return (cost_function, cost_function_derivative_combined)
    @property
    def dimension(self):
        return self._dimension