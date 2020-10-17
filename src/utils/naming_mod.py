# Define names to be used throughout the code. All names that are referenced 
# within multiple functions should be defined in this module.
# Recommended to import as "import naming_mod as names"
# Hence, the variables will not contain name, and will be written as e.g. 
# names.step0

# Model, job and odb naming
model = 'rollover'
job = model

# Part, instance and section names
wheel_part = 'WHEEL'
rail_part = 'RAIL'
wheel_inst = wheel_part
rail_inst = rail_part
rail_sect = rail_part
rail_shadow_sect = 'SHADOW_RAIL'
wheel_dummy_contact_sect = 'WHEEL_DUMMY_CONTACT'

# Sets
wheel_contact_surf = 'WHEEL_CONTACT_SURFACE'
wheel_rp_set = 'RP'
wheel_contact_nodes = 'CONTACT_NODES'
rail_contact_nodes = 'CONTACT_NODES'
rail_contact_surf = 'RAIL_CONTACT_SURFACE'
rail_bottom_nodes = 'BOTTOM_NODES'
rail_set = 'RAIL_SET'
rail_side_sets = ['SIDE1_SET', 'SIDE2_SET']

# BC and interactions
fix_rail_bc = 'FIX_BOTTOM'
wheel_ctrl_bc = 'WHEEL_CTRL'
wheel_vert_load = 'WHEEL_VLOAD'
contact = 'CONTACT'

# Step naming
# Formatting of names
def cycle_str(cycle_nr):    # Format cycle nr
    return str(cycle_nr).zfill(5)
    
step0 = 'Initial'   # Abaqus default
step1 = 'Preload'   # Apply fixed displacement
step2 = 'Loading'   # Apply the contact normal load

def get_step_rolling(cycle_nr=1):
    return 'rolling_' + cycle_str(cycle_nr)
    
def get_step_return(cycle_nr=2):
    return 'return_' + cycle_str(cycle_nr)
    
def get_step_reapply(cycle_nr=2):
    return 'reapply_' + cycle_str(cycle_nr)
    
def get_step_release(cycle_nr=2):
    return 'release_' + cycle_str(cycle_nr)