""" Functions to be called from plugins

"""
from __future__ import print_function
import shutil

from abaqus import mdb
from abaqusConstants import *

from rollover.utils import naming_mod as names
from rollover.utils import abaqus_python_tools as apt
from rollover.three_d.rail import basic as rail_basic
from rollover.three_d.rail import mesher as rail_mesh
from rollover.three_d.utils import symmetric_mesh_module as sm

from rollover.three_d.wheel import substructure as wheel_substr
from rollover.three_d.wheel import super_element as super_wheel

from rollover.three_d.rail import include as rail_include
from rollover.three_d.wheel import include as wheel_include
from rollover.three_d.utils import contact
from rollover.three_d.utils import loading
from rollover.three_d.utils import odb_output
from rollover.three_d.utils import fil_output



def create_rail(profile, name, length, mesh_size, 
                r_x_min, r_y_min, r_x_max, r_y_max, r_x, r_y, sym_sign=0):
    """Create a rail model from plugin input
    
    :param profile: Path to an Abaqus sketch profile saved as .sat file 
                    (acis)
    :type profile: str
    
    :param name: Name of file to save rail as
    :type name: str
    
    :param length: Length of rail to be extruded
    :type length: float
    
    :param mesh_size: Mesh size to be used
    :type mesh_size: float
    
    :param r_x_min: x-coordinate of refinement cell corner nr 1. The 
                    refinement cell also specifies the contact region
    :type r_x_min: float
    
    :param r_y_min: y-coordinate of refinement cell corner nr 1
    :type r_y_min: float
    
    :param r_x_max: x-coordinate of refinement cell corner nr 2
    :type r_x_max: float
    
    :param r_y_max: y-coordinate of refinement cell corner nr 2
    :type r_y_max: float
    
    :param r_x: x-coordinate of point within refinement cell
    :type r_x: float
    
    :param r_y: y-coordinate of point within refinement cell
    :type r_y: float
    
    :param sym_sign: Direction of symmetry normal (along x-axis), if 0
                     no symmetry is applied.
    :type sym_sign: int
    
    """
    
    refinement_cell = [[r_x_min, r_y_min], [r_x_max, r_y_max]]
    point_in_refine_cell = [r_x, r_y, length/2.0]
    sym_dir = None if sym_sign == 0 else [sym_sign, 0, 0]
    rail_model = rail_basic.create(profile, length, 
                                   refine_region=refinement_cell, 
                                   sym_dir=sym_dir)
    rail_part = rail_model.parts[names.rail_part]
    rail_mesh.create_basic(rail_part, point_in_refine_cell, 
                           fine_mesh=mesh_size, coarse_mesh=mesh_size)

    mdb.saveAs(pathName=name)
    
    
def periodicize_mesh():
    """ Attempt to make the mesh periodic between the sides.
    """
    the_model = mdb.models[names.rail_model]
    rail_part = the_model.parts[names.rail_part]
    
    sm.make_periodic_meshes(rail_part, 
                            source_sets=[rail_part.sets[names.rail_side_sets[0]]], 
                            target_sets=[rail_part.sets[names.rail_side_sets[1]]])
    
    rail_part.generateMesh()
    
    
def create_wheel(profile, name, mesh_fine, mesh_coarse, quadratic,
                 c_ang_min, c_ang_max, c_x_min, c_x_max, partition_r):
    """Create a wheel super element from plugin input
    
    :param profile: Path to an Abaqus sketch profile saved as .sat file 
                    (acis)
    :type profile: str
    
    :param name: Name of file to save wheel as
    :type name: str
    
    :param mesh_fine: Fine mesh size (contact surface)
    :type mesh_fine: float
    
    :param mesh_coarse: Coarse mesh size (inside partition_r)
    :type mesh_coarse: float
    
    :param quadratic: Use quadratic elements? (0=false, 1=true)
    :type quadratic: int
    
    :param c_ang_min: Lowest angle to include in contact
    :type c_ang_min: float
    
    :param c_ang_max: Largest angle to include in contact
    :type c_ang_max: float
    
    :param c_x_min: Minimum x-coordinate to include in contact/retain
    :type c_x_min: float
    
    :param c_x_max: Maximum x-coordinate to include in contact/retain
    :type c_x_max: float
    
    :param partition_r: Radius outside which to use the fine mesh
    :type partition_r: float
    
    """
    
    # Create wheel parameter dictionary 
    wheel_param = {'wheel_profile': profile, 
                   'mesh_sizes': [mesh_fine, mesh_coarse],
                   'quadratic_order': quadratic == 1,
                   'wheel_contact_pos': [c_x_min, c_x_max],
                   'wheel_angles': [c_ang_min, c_ang_max],
                   'partition_line': partition_r}
    
    # Create wheel substructure
    job = wheel_substr.generate(wheel_param)
    job.submit()
    job.waitForCompletion()
    
    # Save resulting file
    mdb.saveAs(pathName=name + '.cae')
    
    # Check that analysis succeeded
    if job.status != COMPLETED:
        raise Exception('Abaqus job failed, please see ' + job.name + '.log')
        
    # Create super element files
    super_wheel.get_uel_mesh(wheel_param['quadratic_order'])
    
    # Copy all relevant files to specified directory (name)
    if os.path.exists(name):
        shutil.rmtree(name)
    os.mkdir(name)

    for file_name in [names.uel_stiffness_file, 
                      names.uel_coordinates_file, 
                      names.uel_elements_file,
                      name + '.cae']:
        shutil.copy(file_name, name)

def create_rollover(rail, shadow, use_rp, wheel, trans, stiffness,
                    mu, k_c, uz_init, t_ib, n_inc_ib, L_roll, R_roll, 
                    max_incr, min_incr, N,
                    cycles, load, speed, slip, rail_ext, output_table):
    """
    :param rail: path to rail .cae file 
    :type rail: str
    
    :param shadow: How far to extend shadow region in negative/positive
                   direction. Given as csv
    :type shadow: str
    
    :param use_rp: Use a rail reference point? (0:false,1:true)
    :type use_rp: int
    
    :param wheel: path to wheel folder
    :type wheel: str
    
    :param trans: wheel translation to position before starting (csv)
    :type trans: str
    
    :param stiffness: Young's modulus for wheel
    :type stiffness: float
    
    :param mu: friction coefficient
    :type mu: float
    
    :param k_c: contact stiffness (N/mm^3)
    :type k_c: float
    
    :param uz_init: Initial depression, before changing to load control
    :type uz_init: float
    
    :param t_ib: Step time inbetween rolling steps
    :type t_ib: float
    
    :param n_inc_ib: Maximum number of increments for inbetween steps
    :type n_inc_ib: int
    
    :param L_roll: Rolling length / rail length
    :type L_roll: float
    
    :param R_roll: Rolling radius (used to convert slip to rot. speed)
    :type R_roll: float
    
    :param max_incr: Maximum number of increments
    :type max_incr: int
    
    :param min_incr: Minimum number of increments
    :type min_incr: int
    
    :param N: Number of cycles to simulate
    :type N: int
    
    :param cycles: Which cycles load parameters are specified for. 1 
                   must be included, given as csv
    :type cycles: str
    
    :param load: Wheel load, one value for each specified cycle in 
                 cycles. Given as csv.
    :type load: str
    
    load, speed, slip, rail_ext, output_table
    
    :param speed: Wheel speed, one value for each specified cycle in 
                  cycles. Given as csv.
    :type speed: str
    
    :param slip: Wheel slip, one value for each specified cycle in 
                 cycles. Given as csv.
    :type slip: str
    
    :param rail_ext: Rail extension, one value for each specified cycle
                     in cycles. Given as csv.
    :type rail_ext: str
    
    :param output_table: Field output data specification. Each item 
                         should contain: tuple(field output name, set,
                         variables, frequency, cycle) where the two last
                         are integers and the former are strings. 
    :type output_table: tuple
    
    :returns: None
    
    """
    def get_csv(csv, type):
        if type==str:
            return [str(itm).strip() for itm in csv.split(',')]
        else:
            return [type(itm) for itm in csv.split(',')]
        
    rp = {'model_file': rail,
          'shadow_extents': get_csv(shadow, float),
          'use_rail_rp': use_rp==1}
    wp = {'folder': wheel,
          'translation': get_csv(trans, float),
          'stiffness': stiffness}
          
    cp = {'friction_coefficient': mu,
          'contact_stiffness': k_c}
            
    lp = {'initial_depression': uz_init,
          'inbetween_step_time': t_ib,
          'inbetween_max_incr': n_inc_ib,
          'rolling_length': L_roll,
          'rolling_radius': R_roll,
          'max_incr': max_incr,
          'min_incr': min_incr,
          'num_cycles': N,
          'cycles': get_csv(cycles, int),
          'vertical_load': get_csv(load, float),
          'speed': get_csv(speed, float),
          'slip': get_csv(slip, float),
          'rail_ext': get_csv(rail_ext, float)}
          
        
    # Create model
    rollover_model = apt.create_model(names.model)
    
    # Include rail
    num_nodes, num_elems = rail_include.from_file(rollover_model, **rp)
    
    # Include wheel
    start_lab = (num_nodes+1, num_elems+1)
    wheel_stiffness = wheel_include.from_folder(rollover_model, 
                                                start_labels=start_lab,
                                                **wp)
    # Setup contact
    contact.setup(rollover_model, **cp)
    
    # Setup loading
    num_cycles = loading.setup(rollover_model, **lp)
    
    # Setup field outputs (if requested)
    if len(output_table) > 0:
        heads = ['set', 'var', 'freq', 'cycle']
        op = {}
        for row in output_table:
            op[row[0]] = {}
            for head, val in zip(heads, row[1:]):
                if head == 'var':
                    op[row[0]][head] = get_csv(val, str)
                else:
                    op[row[0]][head] = val
                
        #op = {row[0]: {head:val for head, val in zip(heads, row[1:])} 
        #      for row in output_table}
        odb_output.add(rollover_model, op, num_cycles)
    
    # Add wheel uel to input file
    wheel_include.add_wheel_super_element_to_inp(rollover_model, 
                                                 wheel_stiffness, 
                                                 wp['folder'],
                                                 wp['translation'])
    # Add output to .fil file
    fil_output.add(rollover_model, num_cycles)
    
    # Write reference point coordinates to file:
    with open(names.rp_coord_file, 'w') as fid:
        rail_rp_coord = [0,0,0]
        wheel_rp_coord = wp['translation']
        fid.write(('%25.15e'*3 + '\n') % tuple(wheel_rp_coord))
        fid.write(('%25.15e'*3 + '\n') % tuple(rail_rp_coord))
    
    # Save model database
    mdb.saveAs(pathName=names.model)
    
    # Write input file
    the_job = mdb.Job(name=names.job, model=names.model)
    the_job.writeInput(consistencyChecking=OFF)
    

