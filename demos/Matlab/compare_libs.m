clear all;
addpath(genpath('../../src_matlab'));
%%
step_size=0.05;

% Q and R matrixes determined by the control engineer.
Q = diag([1. 1. 1.])*0.2;
R = diag([1. 1.]) * 0.01;

Q_terminal = diag([1. 1. 1])*10;
R_terminal = diag([1. 1.]) * 0.01;

controller_folder_name = 'demo_controller_matlab';
trailer_controller = prepare_demo_trailer(controller_folder_name,step_size,Q,R,Q_terminal,R_terminal);

trailer_controller.horizon = 40; % NMPC parameter
trailer_controller.integrator_casadi = true; % optional  feature that can generate the integrating used  in the cost function
trailer_controller.panoc_max_steps = 2000; % the maximum amount of iterations the PANOC algorithm is allowed to do.
trailer_controller.min_residual=-3;
trailer_controller.lbgfs_buffer_size=50;
% trailer_controller.pure_prox_gradient=true;

% construct left circle
circle1 = nmpccodegen.controller.obstacles.Obstacle_circular([1.5; 0.], 1.);
circle2 = nmpccodegen.controller.obstacles.Obstacle_circular([3.5; 2.], 0.6);
circle3 = nmpccodegen.controller.obstacles.Obstacle_circular([2.; 2.5], 0.8);
circle4 = nmpccodegen.controller.obstacles.Obstacle_circular([5.; 4.], 1.05);

% add obstacles to controller
trailer_controller = trailer_controller.add_obstacle(circle1);
trailer_controller = trailer_controller.add_obstacle(circle2);
trailer_controller = trailer_controller.add_obstacle(circle3);
trailer_controller = trailer_controller.add_obstacle(circle4);

% generate the dynamic code
trailer_controller = trailer_controller.generate_code();

% simulate everything
initial_state = [0.; -0.5 ; pi/2];
reference_state = [7.; 5.; 0.8];
reference_input = [0; 0];

obstacle_weights = [700.;700.;700.;700.];
%%
[state_history,time_history,iteration_history,simulator] = simulate_demo_trailer(trailer_controller,initial_state,reference_state,reference_input,obstacle_weights);
%%
[state_history_forbes,time_history_forbes,iteration_history_forbes] = simulate_demo_trailer_panoc_matlab(trailer_controller,simulator,initial_state,reference_state,reference_input);
%%
[state_history_fmincon,time_history_fmincon_interior_point] = simulate_demo_trailer_fmincon('interior-point',trailer_controller,simulator,initial_state,reference_state,reference_input);
%%
[~,time_history_fmincon_sqp] = simulate_demo_trailer_fmincon('sqp',trailer_controller,simulator,initial_state,reference_state,reference_input);
%%
[~,time_history_fmincon_active_set] = simulate_demo_trailer_fmincon('active-set',trailer_controller,simulator,initial_state,reference_state,reference_input);
%%
[ state_history_ipopt,time_history_ipopt ]  = simulate_demo_trailer_OPTI_ipopt( trailer_controller,simulator, ...
    initial_state,reference_state,reference_input,obstacle_weights );
%%
% [ state_history_,time_history_ ] = simulate_demo_trailer_casadi_ipopt( trailer_controller, ...
%     initial_state,reference_state,reference_input,obstacle_weights );
%%
figure;
hold on;
nmpccodegen.example_models.trailer_printer(state_history,0.03,'red');
nmpccodegen.example_models.trailer_printer(state_history_forbes,0.03,'black');
nmpccodegen.example_models.trailer_printer(state_history_fmincon,0.03,'blue');
% nmpccodegen.example_models.trailer_printer(state_history_ipopt,0.03,'green');

circle1.plot();
circle2.plot();
circle3.plot();
circle4.plot();
ylabel('y coordinate');
xlabel('x coordinate');
title('black = Forbes red=nmpc-codegen blue=fmincon interior point');
%%
figure;
set(gca, 'YScale', 'log')
hold on;
semilogy(time_history);
semilogy(time_history_forbes);
semilogy(time_history_fmincon_interior_point);
semilogy(time_history_fmincon_sqp);
semilogy(time_history_fmincon_active_set);
semilogy(time_history_ipopt);
ylabel('time till convergence (ms)');
xlabel('step');
legend('nmpc-codegen','ForBEs: zeropfr2','fmincon: interior-point','fmincon: sqp','fmincon: active-set','OPTI toolbox: ipopt');
%%
figure;
hold on;
plot(iteration_history);
plot(iteration_history_forbes);
ylabel('number of iterations till convergence ');
xlabel('step');
legend('nmpc-codegen','ForBEs');