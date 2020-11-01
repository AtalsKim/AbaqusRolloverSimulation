module uel_stiff_mod
implicit none
    
    character(len=20), parameter        :: uel_stiffness_file_name = 'uel_stiffness.txt'
    
    double precision, allocatable, save :: uel_stiffness(:,:)
    
    contains
    
subroutine allocate_uel_stiffness(scale_factor)
use usub_utils_mod, only : get_fid
implicit none
    double precision, intent(in):: scale_factor 
    integer                     :: file_id          ! File identifier
    integer                     :: ndof             ! Number of dofs (read from file)
    integer                     :: i, j             ! Iterators
    integer                     :: check_i, check_j
    double precision            :: tmp

    call get_fid(uel_stiffness_file_name, file_id)
    
    ! The number of dofs is written on the first line as a single integer
    read(file_id, *) ndof
    
    ! Allocate the stiffness
    allocate(uel_stiffness(ndof, ndof))
    
    do i=1,ndof
        do j=i,ndof
            read(file_id, *) uel_stiffness(i, j)
            uel_stiffness(i, j) = uel_stiffness(i, j)*scale_factor
            uel_stiffness(j, i) = uel_stiffness(i, j)
            ! To check that current setup provides correct indices
            ! Requires to modify output from python scripts to include indices
            !read(file_id, *) check_i, check_j, tmp
            !if (i /= check_i) write(*, *) j, '/=', check_i, '(check i)'
            !if (j /= check_j) write(*, *) j, '/=', check_j, '(check j)'
            !uel_stiffness(i, j) = tmp
            !uel_stiffness(j, i) = tmp
        enddo
    enddo
    
end subroutine allocate_uel_stiffness
    

end module uel_stiff_mod