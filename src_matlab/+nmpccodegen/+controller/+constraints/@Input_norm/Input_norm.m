classdef Input_norm < nmpccodegen.controller.constraints.Constraint
    %RECTANGLE Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        max_norm
    end
    
    methods
        function obj = Input_norm(max_norm)
            obj.max_norm=max_norm;
        end
        function cost = evaluate_cost(obj,state,input)
            norm_input = sum1(input.^2);
            cost = max(norm_input - obj.max_norm^2,0)^2; % if norm is higer then max_norm return penalty
        end        
    end
    
end