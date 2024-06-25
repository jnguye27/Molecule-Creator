# Student Name: Jessica Nguyen
# Student ID: 1169812
# Due Date: April 5th, 2023 
# Course: CIS*2750 

import molecule

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500

class Atom:
    # Atom constructor
    def __init__ ( self, c_atom ):
        # Declare and initialize the atom class/struct as a member variable
        self.atom = c_atom

        # Declare and initialize a member variable, z, to be the value in the wrapped class/struct
        self.z = self.atom.z

    # Returns a string that displays the element, x, y, and z values of the wrapped atom
    def __str__ ( self ):
        return 'element = %s, x = %.4f, y = %.4f, z = %.4f' % (self.atom.element, self.atom.x, self.atom.y, self.z)

    # Returns the .svg circle representation of atom
    def svg ( self ):
        # Declaring and initalizing variables
        self.cx = (self.atom.x * 100) + offsetx
        self.cy = (self.atom.y * 100) + offsety
        self.r = radius[self.atom.element]
        self.fill = element_name[self.atom.element]

        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.cx, self.cy, self.r, self.fill)

class Bond: 
    # Bond constructor
    def __init__ ( self, c_bond ):
        # Declare and initialize the bond class/struct as a member variable
        self.bond = c_bond

        # Declare and initialize a member variable, z, to be the value in the wrapped class/struct
        self.z = self.bond.z
    
    # Returns a string that displays the items of the wrapped bond
    def __str__ ( self ):
        return 'epairs = %s, a1 = %d, a2 = %d, x1 = %.4f, y1 = %.4f, x2 = %.4f, y2 = %.4f, z = %.4f, len = %.4f, dx = %.4f, dy = %.4f' % ( self.bond.epairs, self.bond.a1, self.bond.a2, self.bond.x1, self.bond.y1, self.bond.x2, self.bond.y2, self.z, self.bond.len, self.bond.dx, self.bond.dy )

    # Returns the .svg bond / polygon / line segment representation between atoms
    def svg ( self ):
        # Declaring and initalizing variables
        self.px1 = ((self.bond.x1 * 100) + offsetx) + (self.bond.dy*10)
        self.py1 = ((self.bond.y1 * 100) + offsety) - (self.bond.dx*10)

        self.px2 = ((self.bond.x1 * 100) + offsetx) - (self.bond.dy*10)
        self.py2 = ((self.bond.y1 * 100) + offsety) + (self.bond.dx*10)

        self.px3 = ((self.bond.x2 * 100) + offsetx) - (self.bond.dy*10)
        self.py3 = ((self.bond.y2 * 100) + offsety) + (self.bond.dx*10)

        self.px4 = ((self.bond.x2 * 100) + offsetx) + (self.bond.dy*10)
        self.py4 = ((self.bond.y2 * 100) + offsety) - (self.bond.dx*10)

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % ( self.px1, self.py1, self.px2, self.py2, self.px3, self.py3, self.px4, self.py4 )

class Molecule ( molecule.molecule ):
    # Prints out the bonds and the atoms in the molecule for debugging
    def __str__ ( self ):
        for i in range(self.atom_no):
            self.atom = Atom(self.get_atom(i))
            print(self.atom.__str__())

        for j in range(self.bond_no):
            self.bond = Bond(self.get_bond(j))
            print(self.bond.__str__())

    # Orders atoms/bonds to see them correctly in 3d space (.svg image)
    def svg ( self ):
        # Declare and initialize member variables
        i = j = 0
        self.svgArray = ""
        self.finalString = ""
        self.a1 = Atom(self.get_atom(0))
        self.b1 = Bond(self.get_bond(0))

        # Mergesort the z values in atoms and bonds (assuming both are presorted)
        while i < self.atom_no and j < self.bond_no:
            if self.a1.z < self.b1.z:
                self.svgArray += self.a1.svg()
                i += 1
                if i < self.atom_no:
                    self.a1 = Atom(self.get_atom(i))
            else: # b1.z < a1.z
                self.svgArray += self.b1.svg()
                j += 1
                if j < self.bond_no:
                    self.b1 = Bond(self.get_bond(j))
        
        # If one list is completed, put all of the other list into the svgArray
        if i == self.atom_no:
            while j < self.bond_no:
                self.svgArray += self.b1.svg()
                j += 1
                if j < self.bond_no:
                    self.b1 = Bond(self.get_bond(j))
        else:
            while i < self.atom_no:
                self.svgArray += self.a1.svg()
                i += 1
                if i < self.atom_no:
                    self.a1 = Atom(self.get_atom(i))

        # Merge all of the parts together
        self.finalString += header
        self.finalString += self.svgArray
        self.finalString += footer

        # Return the final result
        return self.finalString

    # Parses the data from a folder into a molecule object
    def parse ( self, fp ):
        # Puts the entire file into multiple lines (an array)
        self.multipleLines = fp.readlines()

        # Gets rid of the first 3 lines in the .sdf file
        self.line = self.multipleLines.pop(0)
        self.line = self.multipleLines.pop(0)
        self.line = self.multipleLines.pop(0)

        # Splits the parts of one line into another array and gets rid of the extra spaces inbetween
        self.line = self.multipleLines.pop(0).split()

        # Converts atom/bond total from strings to ints
        self.amountOfAtom = int(self.line[0])
        self.amountOfBond = int(self.line[1])

        # Takes one line at a time and appends the data found
        for i in range(self.amountOfAtom):
            self.line = self.multipleLines.pop(0).split()
            self.append_atom(self.line[3], float(self.line[0]), float(self.line[1]), float(self.line[2]))

        for j in range(self.amountOfBond):
            self.line = self.multipleLines.pop(0).split()
            self.append_bond(int(self.line[0])-1, int(self.line[1])-1, int(self.line[2]))
