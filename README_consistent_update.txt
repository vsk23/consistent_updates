To launch the consistent_updates module you must add it as a module to the pox launch command: 
    Ex: /home/mininet/pox/pox.py consistent_update …OTHER MODULES..



module files:
    consistent_update.py - contains the update functionality
    configuration.py - Represents the configuration object. ( List of flow mods)

case study files: 
    shortpath.py
    shortpath_app.py
    updator.py
Case study files also demonstrate example usage. Shortpath implements Djikstra's and generates flow mods representing shortest paths. This is then returned as a configuration object and can be used by consistent_update to update the switches. Transitions between topologies represent consistent update transitions.

test topologies:
    short_path_one.py
    short_path_two.py
Topologies that were used with the short path application. 

launch shortpath:
    Ex: /home/mininet/pox/pox.py openflow.topology openflow.discovery topology optimizations shortpath shortpath_app consistent_update 



Example Usage:

    configuration = Configuration()
    switch_id = 1
    match = of.ofp_match(in_port = 1)
    flow = of.ofp_flow_mod(match = match)
    configuration.add_flow_mod(flow)
    configuration.add_flow_mod(flow,switch_id)
    core.consistent_update.update_config(configuration)



