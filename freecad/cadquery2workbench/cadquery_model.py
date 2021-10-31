""" derived class from cadquery cqgi.py """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import ast
import traceback
import time
from cadquery.cqgi import CQSCRIPT, CQModel, ScriptCallback, BuildResult
from cadquery.cqgi import EnvironmentBuilder, ShapeResult, InputParameter
from cadquery.cqgi import ConstantAssignmentFinder
from cadquery.cqgi import BooleanParameterType, StringParameterType
from cadquery.cqgi import NumberParameterType, NumberParameterType


class CQ_Model(CQModel):
    '''extend Cadquery cqgi.CQModel class.'''

    def __init__(self, script_source):
        '''
        Create an object by parsing the supplied python script.
        
        :param script_source: a python script to parse
        '''
        CQModel.__init__(self, script_source)
        
    def _find_vars(self):
        '''
        Parse the script, and populate variables that appear to be overridable.
        
        Override original one to use updated ConstantAssignmentFinder class.
        '''
        # assumption here: we assume that variable declarations
        # are only at the top level of the script. IE, we'll ignore any
        # variable definitions at lower levels of the script

        # we don't want to use the visit interface because here we explicitly
        # want to walk only the top level of the tree.
        assignment_finder = Constant_Assignment_Finder(self.metadata)           # Updated line

        for node in self.ast_tree.body:
            if isinstance(node, ast.Assign):
                assignment_finder.visit_Assign(node)
    
    def build(self, build_parameters=None, build_options=None):
        '''
        Executes the script, using the optional parameters to override those in the model.
        
        Override original one to use updated ScriptCallback class.
        
        :param build_parameters: a dictionary of variables. The variables must be
        assignable to the underlying variable type. These variables override default values in the script
        :param build_options: build options for how to build the model. Build options include things like
        timeouts, tessellation tolerances, etc
        
        :raises: Nothing. If there is an exception, it will be on the exception property of the result.
        This is the interface so that we can return other information on the result, such as the build time
        
        :return: a BuildResult object, which includes the status of the result, and either
        a resulting shape or an exception
        '''

        if not build_parameters:
            build_parameters = {}
        
        start = time.perf_counter()
        result = BuildResult()

        try:
            self.set_param_values(build_parameters)
            collector = Script_Callback()                                       # Updated line
            env = (
                EnvironmentBuilder()
                .with_real_builtins()
                .with_cadquery_objects()
                .add_entry("__name__", "__cqgi__")
                .add_entry("show_object", collector.show_object)
                .add_entry("debug", collector.debug)
                .add_entry("describe_parameter", collector.describe_parameter)
                .build()
            )

            c = compile(self.ast_tree, CQSCRIPT, "exec")
            exec(c, env)
            result.set_debug(collector.debugObjects)
            result.set_success_result(collector.outputObjects)
            result.env = env
            
        except Exception as ex:
            result.set_failure_result(ex)
            
        end = time.perf_counter()
        result.buildTime = end - start
        
        return result
        

class Script_Callback(ScriptCallback):
    '''
    extend Cadquery cqgi.ScriptCallback class.
    
    Allows a script to communicate with the container
    the show_object() method is exposed to CQ scripts, to allow them
    to return objects to the execution environment
    '''
    
    def __init__(self):
        ScriptCallback.__init__(self)
    
    def show_object(self, shape, options=None, **kwargs):
        '''
        Override original one. Return an object to the executing environment, with options.
        
        :param shape: a cadquery object
        :param options: a dictionary of options that will be made available to the executing environment
        :param **kwargs: allow to pass option as a list of pair key=value
        '''
        if options == None:
            options = {}
        options.update(kwargs)
        
        o = ShapeResult()
        o.options = options
        o.shape = shape
        self.outputObjects.append(o)
    
    def debug(self, shape, options=None, **kwargs):
        '''
        Override original one. Debug print/output an object, with optional arguments.
        
        :param shape: a cadquery object
        :param options: a dictionary of options that will be made available to the executing environment
        :param **kwargs: allow to pass option as a list of pair key=value
        '''
        if options == None:
            options = {}
        options.update(kwargs)
        
        s = ShapeResult()
        s.options = options
        s.shape = shape
        self.debugObjects.append(s)
        
    def describe_parameter(self, varname, desc):
        '''
        Override original one. Do Nothing-- we parsed the ast ahead of execution to get what we need.
        
        update to 2 arguments instead of 1 in cqgi.py
        '''
        pass
        

class Constant_Assignment_Finder(ast.NodeTransformer):
    """
    override Cadquery cqgi.ConstantAssignmentFinder class.
    
    Visits a parse tree, and adds script parameters to the cqModel
    Update to parse the variables setting using cqvar(value, description) method
    """

    def __init__(self, cq_model):
        self.cqModel = cq_model

    def handle_assignment(self, var_name, value_node, value_desc=None):
        
        try:

            if type(value_node) == ast.Num:
                self.cqModel.add_script_parameter(
                    InputParameter.create(
                        value_node, var_name, NumberParameterType, value_node.n
                    )
                )
            elif type(value_node) == ast.Str:
                self.cqModel.add_script_parameter(
                    InputParameter.create(
                        value_node, var_name, StringParameterType, value_node.s
                    )
                )
            elif type(value_node) == ast.Name:
                if value_node.id == "True":
                    self.cqModel.add_script_parameter(
                        InputParameter.create(
                            value_node, var_name, BooleanParameterType, True
                        )
                    )
                elif value_node.id == "False":
                    self.cqModel.add_script_parameter(
                        InputParameter.create(
                            value_node, var_name, BooleanParameterType, False
                        )
                    )
            elif hasattr(ast, "NameConstant") and type(value_node) == ast.NameConstant:
                if value_node.value == True:
                    self.cqModel.add_script_parameter(
                        InputParameter.create(
                            value_node, var_name, BooleanParameterType, True
                        )
                    )
                else:
                    self.cqModel.add_script_parameter(
                        InputParameter.create(
                            value_node, var_name, BooleanParameterType, False
                        )
                    )

            elif hasattr(ast, "Constant") and type(value_node) == ast.Constant:

                type_dict = {
                    bool: BooleanParameterType,
                    str: StringParameterType,
                    float: NumberParameterType,
                    int: NumberParameterType,
                }
                self.cqModel.add_script_parameter(
                    InputParameter.create(
                        value_node,
                        var_name,
                        type_dict[type(value_node.value)],
                        value_node.value,
                    )
                )
            
            if value_desc:
                self.cqModel.add_parameter_description(var_name, value_desc)
            
        except:
            print("Unable to handle assignment for variable '%s'" % var_name)
            pass

    def visit_Assign(self, node):

        try:
            left_side = node.targets[0]

            # do not handle attribute assignments
            if isinstance(left_side, ast.Attribute):
                return

            # Handle the NamedConstant type that is only present in Python 3
            astTypes = [ast.Num, ast.Str, ast.Name]
            if hasattr(ast, "NameConstant"):
                astTypes.append(ast.NameConstant)

            if hasattr(ast, "Constant"):
                astTypes.append(ast.Constant)

            if type(node.value) in astTypes:
                self.handle_assignment(left_side.id, node.value)
            
            elif type(node.value) == ast.Tuple:
                # we have a multi-value assignment
                for n, v in zip(left_side.elts, node.value.elts):
                    self.handle_assignment(n.id, v)
            
            elif type(node.value) == ast.Call:
                try:
                    if node.value.func.id == "cqvar":
                        self.handle_assignment(left_side.id, node.value.args[0],
                                                node.value.args[1].s)
                except:
                    pass
            
        except:
            traceback.print_exc()
            print("Unable to handle assignment for node '%s'" % ast.dump(left_side))

        return node
