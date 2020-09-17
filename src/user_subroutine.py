# Module used to import and compile user subroutines
# The strategy is to collect all files required to generate subroutines in a folder called "usub" in
# the current working directory. A usub.for/.f file is then included that includes all the 
# subroutines put in that folder. 
from __future__ import print_function
import os
import shutil

# These parameters can be accessed via user_subroutine.* to facilitate copying
folder = 'usub'
name = 'usub'
fortran_suffix = '.for' if os.name == 'nt' else '.f'
# If they exist, the following files (excluding suffix), will be made into one subroutine
supported_usubs = ['umat', 'uel', 'disp', 'urdfil'] 


def setup():
    # In the beginning of a rollover simulation, setup should be called to create the necessary 
    # folder containing the subroutines
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)


def generate():
    # Before submitting the first abaqus job, the generate routine should be called to create the 
    # necessary fortran files and compile these into a library
    shutil.copy('C:/Users/knutan/Documents/Work/ProjectsWorkFolders/MU34/Project_2020_C_RolloverSimulation/abaqus_fil_test/urdfil.for',
                folder)
    copy_fortran_files_from_cwd()
    create_file()
    make()
    check_abaqus_env()


def copy_all_files_and_folders_from_folder(input_folder):
    # Copy all files and folders in the given input_folder to the usub folder.
    items = os.listdir(input_folder)
    for item in items:
        full_item_path = input_folder + '/' + item
        if os.path.isdir(full_item_path):
            shutil.copytree(full_item_path, folder + '/' + item)
        else:
            shutil.copy(full_item_path, folder)


def copy_fortran_files_from_cwd():
    files_and_folders_in_cwd = os.listdir('.')
    for file in files_and_folders_in_cwd:
        if fortran_suffix in file:
            shutil.copy(file, folder + '/')


def create_file():
    usubs = [sub + fortran_suffix for sub in supported_usubs]
    usub_name = name + fortran_suffix
    all_files_and_folders = os.listdir(folder)
    usub_str = '!DEC$ FREEFORM\n'
    usub_str = usub_str + '! User subroutines for Abaqus Rollover Simulation\n'
    usub_str = usub_str + '! Compile with "abaqus make library=' + usub_name + '\n'
    for file in all_files_and_folders:
        if file in usubs:
            with open(folder + '/' + file, 'r') as fid:
                file_str = fid.read()
                # Following line requried? Is it a problem to have multiple of "!DEC$ FREEFORM"?
                file_str = file_str.replace('!DEC$ FREEFORM', '!')  
                usub_str = usub_str + file_str + '\n'
                
            
    with open(folder + '/' + usub_name, 'w') as fid:
        fid.write(usub_str)


def make():
    os.chdir(folder)
    
    shared_lib = 'standardU.dll' if os.name == 'nt' else 'libstandard.so'
    object_file = (name + '-std.obj') if os.name == 'nt' else (name + '-std.o')
    
    # Remove any old compiled files
    for file in [shared_lib, object_file]:
        if os.path.exists(file):
            os.remove(file)
    
    # Compile new files and move shared library to simulation directory
    os.system('abaqus make library=' + name)
    shutil.copy(shared_lib, '..')
        
    os.chdir('..')


def check_abaqus_env():
    # Function to check that the env file contains usub_lib_dir pointing to the working directory.
    # -If the abaqus_v6.env doesn't exist in cwd, create an empty one
    # - And if it doesn't contain usub_lib_dir, add the cwd.
    # - Or, if it contains usub_lib_dir pointing to another folder, comment out that line and add a 
    #   new line with the correct path. (Note, should eval expression in python to get result)
    print('Warning: No check for abaqus_v6.env implemented in user_subroutine.py')