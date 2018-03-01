classdef IndicatorBoxFunction < ProximalFunction
    %INDICATORBOXFUNCTION Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        lower_limits
        upper_limits
        dimension
    end
    
    methods
        function obj=IndicatorBoxFunction(lower_limits,upper_limits)
            obj@ProximalFunction();
            
            obj.lower_limits=lower_limits;
            obj.upper_limits=upper_limits;
            obj.dimension = min(length(lower_limits),length(upper_limits));
            
            obj.prox = IndicatorBoxFunctionProx(lower_limits,upper_limits);
        end
        function obj=generate_c_code(obj, location)
            source_file = Source_file_generator(location,'g');
            source_file = source_file.open();
            source_file = source_file.start_for('i','MPC_HORIZON',1);
            
            for i_dimension=1:obj.dimension
                source_file.write_comment_line('check if the value of the border is outside the box, if so return zero', ...
                                               2);
                source_file = source_file.write_line( ['if(state[' num2str(i_dimension-1) ...
                    ']<' num2str(obj.lower_limits(i_dimension)) ...
                    ' || state[' num2str(i_dimension-1) ']>' ... 
                    num2str(obj.upper_limits(i_dimension))  ...
                    '){'],2);
                source_file = source_file.write_line('return LARGE;',3);
                source_file = source_file.write_line('}',2);
            end
            
            source_file = source_file.write_line(['state+=' num2str(obj.dimension) ';'],2);
            source_file = source_file.close_for(1);

            source_file = source_file.write_comment_line('if the values where never outside the box, return zero',1);
            source_file = source_file.write_line( 'return 0;', 1);
            source_file.close();
        end
    end
    
end