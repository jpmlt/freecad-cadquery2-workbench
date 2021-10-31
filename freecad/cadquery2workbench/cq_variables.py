""" to add another way to create cadquery variables with their description """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License

def cqvar(value, description):
    """
    Set cadquery variables value and descritpion.
    
    :param value: the value to be used when executing the script.
    :param description: description of the variable is read when parsing the script
        and returned into the build_parameters of the cqModel.build method.
    """
    return value
    
