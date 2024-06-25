/* 
  Student Name: Jessica Nguyen
  Student ID: 1169812
  Due Date: April 5th, 2023 
  Course: CIS*2750 
*/

// mol.h contains my function code
#include "mol.h"

// atomset copies the values pointed to by element, x, y, and z into the atom stored at atom
void atomset( atom *atom, char element[3], double *x, double *y, double *z )
{
  strcpy(atom->element,element);

  atom->x = *x;
  atom->y = *y;
  atom->z = *z;
}

// atomget copies the values in the atom stored at atom to the locations pointed to by element, x, y, and z
void atomget( atom *atom, char element[3], double *x, double *y, double *z )
{
  strcpy(element,atom->element);

  *x = atom->x;
  *y = atom->y;
  *z = atom->z;
}

// bondset copies the values a1, a2, atoms, and epairs into the corresponding structure attributes in bond
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs )
{
  bond->a1 = *a1;
  bond->a2 = *a2;
  
  bond->atoms = *atoms;
  bond->epairs = *epairs;

  compute_coords( bond );
}

// bondget copies the structure attributes in bond to their corresponding arguments: a1, a2, atoms, and epairs
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs )
{
  *a1 = bond->a1;
  *a2 = bond->a2;

  *atoms = bond->atoms;
  *epairs = bond->epairs;
}

// compute_coords calculates the z, x1, y1, x2, y2, len, dx, and dy values of the specified bond
void compute_coords( bond *bond )
{
  bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z)/2;

  bond->x1 = bond->atoms[bond->a1].x;
  bond->y1 = bond->atoms[bond->a1].y;

  bond->x2 = bond->atoms[bond->a2].x;
  bond->y2 = bond->atoms[bond->a2].y;

  bond->len = sqrt(pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2));

  bond->dx = (bond->x2 - bond->x1) / bond->len;
  bond->dy = (bond->y2 - bond->y1) / bond->len;
}

// molmalloc returns the address of a malloced area of memory, large enough to hold a molecule
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max )
{
  molecule *molecule;
  molecule = NULL;
  molecule = malloc(sizeof(struct molecule));

  // Atom values are inputted into the molecule and pointers/arrays are allocated
  molecule->atom_max = atom_max;
  molecule->atom_no = 0;
  molecule->atoms = (atom*)malloc(sizeof(atom)*(atom_max+1));
  molecule->atom_ptrs = (atom**)malloc(sizeof(atom*)*(atom_max+1));
  
  // Bond values are inputted into the molecule and pointers/arrays are allocated
  molecule->bond_max = bond_max;
  molecule->bond_no = 0;
  molecule->bonds = (bond*)malloc(sizeof(bond)*(bond_max+1));
  molecule->bond_ptrs = (bond**)malloc(sizeof(bond*)*(bond_max+1));

  if (molecule == NULL||molecule->atoms == NULL||molecule->atom_ptrs == NULL||molecule->bonds == NULL||molecule->bond_ptrs == NULL)
  {
    printf("\n\nMemory Allocation Failed.\n\n");
    return NULL;
  }

  return molecule;
}

// molcopy returns the address of a malloced area of memory, large enough to hold a molecule copy
molecule *molcopy( molecule *src )
{
  int i, j;
  molecule *molecule; 

  molecule = molmalloc(src->atom_max, src->bond_max);

  for (i = 0; i < src->atom_no; i++)
  {
    molappend_atom(molecule, &src->atoms[i]);
  }

  for (j = 0; j < src->bond_no; j++)
  {
    molappend_bond(molecule, &src->bonds[j]);
  }

  molecule->atom_no = src->atom_no;
  molecule->bond_no = src->bond_no;
    
  return molecule;
}

// molfree frees the memory associated with the molecule pointed to by ptr
// **Note to self: use valgrind -v ./a1 for any memory leaks
void molfree( molecule *ptr )
{
  free(ptr->bond_ptrs);
  free(ptr->bonds);
  free(ptr->atom_ptrs);
  free(ptr->atoms);
  free(ptr);
}

/* molappend_atom copies the data pointed to by atom to the first “empty” atom in atoms in the
molecule pointed to by molecule, and set the first “empty” pointer in atom_ptrs to the same
atom in the atoms array incrementing the value of atom_no */
void molappend_atom( molecule *molecule, atom *atom )
{
  int i;

  // If atom_max = 0, then add 1
  // If atom_max = atom_no, then multiply atom_max by 2
  if (molecule->atom_max == 0)
  {
    molecule->atom_max = molecule->atom_max+1;
    molecule->atoms = (struct atom*)realloc(molecule->atoms,sizeof(struct atom)*(molecule->atom_max+1));
    molecule->atom_ptrs = (struct atom**)realloc(molecule->atom_ptrs,sizeof(struct atom*)*(molecule->atom_max+1));
  }
  else if (molecule->atom_no == molecule->atom_max)
  {
    molecule->atom_max = molecule->atom_max*2;
    molecule->atoms = (struct atom*)realloc(molecule->atoms,sizeof(struct atom)*(molecule->atom_max+1));
    molecule->atom_ptrs = (struct atom**)realloc(molecule->atom_ptrs,sizeof(struct atom*)*(molecule->atom_max+1));
  }
  
  molecule->atoms[molecule->atom_no] = *atom;

  // Makes sure that the malloced/realloced atom_ptrs point to the new atoms array
  for (i = 0; i <= molecule->atom_no; i++)
  {
    molecule->atom_ptrs[i] = &molecule->atoms[i];
  }
  
  molecule->atom_no = molecule->atom_no + 1;
}

// molappend_bond is similar to molappend_atom but with bonds instead
void molappend_bond( molecule *molecule, bond *bond )
{
  int i;

  // If bond_max = 0, then add 1
  // If bond_max = bond_no, then multiply bond_max by 2
  if (molecule->bond_max == 0)
  {
    molecule->bond_max = molecule->bond_max+1;
    molecule->bonds = (struct bond*)realloc(molecule->bonds,sizeof(struct bond)*(molecule->bond_max+1));
    molecule->bond_ptrs = (struct bond**)realloc(molecule->bond_ptrs,sizeof(struct bond*)*(molecule->bond_max+1));
  }
  else if (molecule->bond_no == molecule->bond_max)
  {
    molecule->bond_max = molecule->bond_max*2;
    molecule->bonds = (struct bond*)realloc(molecule->bonds,sizeof(struct bond)*(molecule->bond_max+1));
    molecule->bond_ptrs = (struct bond**)realloc(molecule->bond_ptrs,sizeof(struct bond*)*(molecule->bond_max+1));
  }
  
  molecule->bonds[molecule->bond_no] = *bond;

  // Makes sure that the malloced/realloced bond_ptrs point to the new bonds array
  for (i = 0; i <= molecule->bond_no; i++)
  {
    molecule->bond_ptrs[i] = &molecule->bonds[i];
  }
  
  molecule->bond_no = molecule->bond_no+1;
}

// Used in molsort for organizing atom_ptrs
int atom_comp( const void *a, const void *b )
{
  atom **a_ptr, **b_ptr;

  a_ptr = (atom **)a;
  b_ptr = (atom **)b;

  // Had to change it since values are doubles but the function returns int
  // Compares a & b, returning a value stating their position validity
  if ((*a_ptr)->z > (*b_ptr)->z)
  {
    return 1;
  }
  else if ((*a_ptr)->z < (*b_ptr)->z)
  {
    return -1;
  }
  else
  {
    return 0;
  }
}

// Used in molsort for organizing bond_ptrs
int bond_comp( const void *a, const void *b )
{
  bond **a_ptr, **b_ptr;

  a_ptr = (bond **)a;
  b_ptr = (bond **)b;
   
  // Had to change it since values are doubles but the function returns int
  // Compares a & b, returning a value stating their position validity
  if ((*a_ptr)->z > (*b_ptr)->z)
  {
    return 1;
  }
  else if ((*a_ptr)->z < (*b_ptr)->z)
  {
    return -1;
  }
  else
  {
    return 0;
  }
}

// molsort sorts atom & bond pointers from low to high z values
// bond z = (atom 1's z + atom 2's z)/2
void molsort( molecule *molecule )
{
  qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom*), atom_comp);
  qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond*), bond_comp);
}

// xrotation sets the values into an affine transformation matrix 
// Corresponds to a rotation of degrees around the x-axis
void xrotation( xform_matrix xform_matrix, unsigned short deg )
{
  // Had to convert degrees into radians
  xform_matrix[0][0] = 1;
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = 0;

  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = cos(deg * (PI/180));
  xform_matrix[1][2] = -sin(deg * (PI/180));

  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = sin(deg * (PI/180));
  xform_matrix[2][2] = cos(deg * (PI/180));
}

// yrotation sets the values into an affine transformation matrix 
// Corresponds to a rotation of degrees around the y-axis
void yrotation( xform_matrix xform_matrix, unsigned short deg )
{
  // Had to convert degrees into radians
  xform_matrix[0][0] = cos(deg * (PI/180));
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = sin(deg * (PI/180));

  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = 1;
  xform_matrix[1][2] = 0;

  xform_matrix[2][0] = -sin(deg * (PI/180));
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = cos(deg * (PI/180));
}

// zrotation sets the values into an affine transformation matrix 
// Corresponds to a rotation of degrees around the z-axis
void zrotation( xform_matrix xform_matrix, unsigned short deg )
{
  // Had to convert degrees into radians
  xform_matrix[0][0] = cos(deg * (PI/180));
  xform_matrix[0][1] = -sin(deg * (PI/180));
  xform_matrix[0][2] = 0;

  xform_matrix[1][0] = sin(deg * (PI/180));
  xform_matrix[1][1] = cos(deg * (PI/180));
  xform_matrix[1][2] = 0;
  
  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = 1;
}

// mol_xform will apply the transformation matrix to all the atoms of the molecule by
// performing a vector matrix multiplication on the x, y, z coordinates
void mol_xform( molecule *molecule, xform_matrix matrix )
{
  char element[3];
  double x,y,z;
  int i;
  atom *atom_ptr;
  bond *bond_ptr;
  
  for (i = 0; i < molecule->atom_no; i++)
  {
    atom_ptr = molecule->atoms + i;
      
    atomget(atom_ptr, element, &x, &y, &z);
      
    // Use matrix multiplication
    atom_ptr->x = (matrix[0][0] * x) + (matrix[0][1] * y) + (matrix[0][2] * z);
    atom_ptr->y = (matrix[1][0] * x) + (matrix[1][1] * y) + (matrix[1][2] * z);
    atom_ptr->z = (matrix[2][0] * x) + (matrix[2][1] * y) + (matrix[2][2] * z);
  }

  for (i = 0; i < molecule->bond_no; i++)
  {
    bond_ptr = molecule->bonds + i;
    compute_coords( bond_ptr );
  }
}
