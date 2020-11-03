module rollover_mod
implicit none
    
    private
    
    public  :: get_step_type
    public  :: STEP_TYPE_INITIAL_DEPRESSION
    public  :: STEP_TYPE_ROLLING
    public  :: STEP_TYPE_MOVE_BACK
    public  :: STEP_TYPE_REAPPLY_LOAD
    public  :: STEP_TYPE_RELEASE_NODES
    
    ! Constants for the get_step_type function:
    integer, parameter  :: STEP_TYPE_INITIAL_DEPRESSION = -1
    integer, parameter  :: STEP_TYPE_ROLLING = 0
    integer, parameter  :: STEP_TYPE_MOVE_BACK = 1
    integer, parameter  :: STEP_TYPE_REAPPLY_LOAD = 2
    integer, parameter  :: STEP_TYPE_RELEASE_NODES = 3
	
    contains
	
	function get_step_type(kstep) result (step_type)
    ! Determine the step type for the given step number, see module constant
    implicit none
        integer, parameter  :: N_STEP_INITIAL = 2   ! Number of initial steps including first rollover
        integer, parameter  :: N_STEP_PER_CYCLE = 4 ! Number of steps per rollover cycle
        
        integer, intent(in) :: kstep                ! Step number
        integer             :: step_type            ! Step type
        
        if (kstep < N_STEP_INITIAL) then
            step_type = -kstep
        else
            step_type = mod(kstep-N_STEP_INITIAL, N_STEP_BETWEEN)
        endif
        
        ! Check result
        if (not(any(step_type == [STEP_TYPE_INITIAL_DEPRESSION, STEP_TYPE_ROLLING, &
                                  STEP_TYPE_MOVE_BACK, STEP_TYPE_REAPPLY_LOAD, &
                                  STEP_TYPE_RELEASE_NODES]))) then
            write(*,"(A,I0,A)") 'Step type = ', step_type, ' not recognized'
            write(*,*) 'usub_utils_mod, get_step_type'
            call xit()
        endif
        
    end function get_step_type


end module rollover_mod