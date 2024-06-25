# Student Name: Jessica Nguyen
# Student ID: 1169812
# Due Date: April 5th, 2023 
# Course: CIS*2750 

import os
import sqlite3
import MolDisplay

class Database:
    # Database Constructor
    def __init__( self, reset ):
        # If reset is True, delete the existing "molecules.db" file first to refresh the database
        if reset == True and os.path.exists( 'molecules.db' ):
            os.remove( 'molecules.db' )
        
        # The constructor opens a database file (or creates it if it doesn't exist) and connects to it
        self.conn = sqlite3.connect( 'molecules.db' )

    # This method creates the tables only if they don't pre-exist
    def create_tables( self ):
        # AUTOINCREMENT works if that column is an INTEGER + PRIMARY KEY
        # VARCHAR = ranging lengths, CHAR = static length
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Elements
                                   ( ELEMENT_NO     INTEGER     NOT NULL,
                                     ELEMENT_CODE   VARCHAR(3)  NOT NULL,
                                     ELEMENT_NAME   VARCHAR(32) NOT NULL,
                                     COLOUR1        CHAR(6)     NOT NULL,
                                     COLOUR2        CHAR(6)     NOT NULL,
                                     COLOUR3        CHAR(6)     NOT NULL,
                                     RADIUS         DECIMAL(3)  NOT NULL,
                                     PRIMARY KEY    (ELEMENT_CODE) );""" )

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Atoms
                                   ( ATOM_ID        INTEGER         NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                                     ELEMENT_CODE   VARCHAR(3)      NOT NULL,
                                     X              DECIMAL(7,4)    NOT NULL,
                                     Y              DECIMAL(7,4)    NOT NULL,
                                     Z              DECIMAL(7,4)    NOT NULL,
                                     FOREIGN KEY    (ELEMENT_CODE) REFERENCES Elements );""" )

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Bonds
                                   ( BOND_ID        INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,   
                                     A1             INTEGER     NOT NULL,
                                     A2             INTEGER     NOT NULL,
                                     EPAIRS         INTEGER     NOT NULL );""" )

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Molecules
                                   ( MOLECULE_ID    INTEGER     NOT NULL    PRIMARY KEY     AUTOINCREMENT,
                                     NAME           TEXT        NOT NULL );""" )
                                    # NAME is suppose to be a unique primary key

        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeAtom
                                   ( MOLECULE_ID    INTEGER     NOT NULL,
                                     ATOM_ID        INTEGER     NOT NULL,
                                     PRIMARY KEY    (MOLECULE_ID, ATOM_ID),
                                     FOREIGN KEY    (MOLECULE_ID) REFERENCES Molecules,
                                     FOREIGN KEY    (ATOM_ID)     REFERENCES Atoms );""" )

        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeBond
                                   ( MOLECULE_ID     INTEGER    NOT NULL,
                                     BOND_ID         INTEGER    NOT NULL,
                                     PRIMARY KEY     (MOLECULE_ID, BOND_ID),
                                     FOREIGN KEY     (MOLECULE_ID) REFERENCES Molecules,
                                     FOREIGN KEY     (BOND_ID) REFERENCES Bonds );""" )
        
        # Newly made tables to keep the selected molecule + molecule elements for display
        self.conn.execute( """CREATE TABLE IF NOT EXISTS SelectedMolecule
                                   ( MOLECULE_NAME    TEXT        NOT NULL );""" )
        self.conn.execute( """CREATE TABLE IF NOT EXISTS PermanentElements
                                   ( ELEMENT_CODE     VARCHAR(3)  NOT NULL );""" )

        # Save database changes
        self.conn.commit()

    # This method sets the values into the table by using indexing (i.e. [key])
    def __setitem__( self, table, values ):
        # If 'values' is not a tuple, turn it into one
        if type(values) is not tuple and table == 'Molecules': 
            self.param = tuple([values])
        elif type(values) is not tuple:
            self.param = (*values,)
        else:
            self.param = values

        # ? allows for different tuple datatypes to be inputted into the table
        if table == 'Elements':
            self.conn.execute( """INSERT INTO Elements ( ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS ) 
            VALUES ( ?, ?, ?, ?, ?, ?, ? );""", self.param )

        elif table == 'Atoms':
            self.conn.execute( """INSERT INTO Atoms ( ELEMENT_CODE, X, Y, Z ) 
            VALUES ( ?, ?, ?, ? );""", self.param )

        elif table == 'Bonds':
            self.conn.execute( """INSERT INTO Bonds ( A1, A2, EPAIRS ) 
            VALUES ( ?, ?, ? );""", self.param )

        elif table == 'Molecules':
            self.conn.execute( """INSERT INTO Molecules ( NAME ) 
            VALUES ( ? );""", self.param )

        elif table == 'MoleculeAtom':
            self.conn.execute( """INSERT INTO MoleculeAtom ( MOLECULE_ID, ATOM_ID ) 
            VALUES ( ?, ? );""", self.param )

        elif table == 'MoleculeBond':
            self.conn.execute( """INSERT INTO MoleculeBond ( MOLECULE_ID, BOND_ID ) 
            VALUES ( ?, ? );""", self.param )

        else: 
            print("%s does not exist", table)
        
        # Save database changes
        self.conn.commit()

    # This method adds atom data into the Atoms & MoleculeAtom table
    def add_atom( self, molname, atom ):
        # Creates an Atom object
        self.atom = MolDisplay.Atom(atom)

        # Turn atom data into a list
        self.atomData = [self.atom.atom.element, self.atom.atom.x, self.atom.atom.y, self.atom.z]

        # Adds the attributes of the atom object to the Atoms table
        self.__setitem__('Atoms', self.atomData)
        
        # Adds an entry into the MoleculeAtom table that links the named molecule to the atom entry in the Atoms table
        self.molID = self.conn.execute( """SELECT DISTINCT MOLECULE_ID FROM Molecules WHERE NAME = '""" + molname + """'""" )
        self.atomID = self.conn.execute( """SELECT DISTINCT ATOM_ID FROM Atoms WHERE ELEMENT_CODE = '""" + self.atom.atom.element + """' AND X = """ + str(self.atom.atom.x) + """ AND Y = """ + str(self.atom.atom.y) + """ AND Z = """ + str(self.atom.z) )
        
        # Gets rid of the extra comma in the fetched data
        self.atomData = [self.molID.fetchone(), self.atomID.fetchone()]
        self.atomData = [self.atomData[0][0], self.atomData[1][0]]

        self.__setitem__('MoleculeAtom', self.atomData)

    # This method adds bond data into the Bonds & MoleculeBond table
    def add_bond( self, molname, bond ):
        # Creates a Bond object
        self.bond = MolDisplay.Bond(bond)

        # Turn bond data into a list
        self.bondData = [self.bond.bond.a1, self.bond.bond.a2, self.bond.bond.epairs]

        # Adds the attributes of the bond object to the Bonds table
        self.__setitem__('Bonds', self.bondData)

        # Adds an entry into the MoleculeBond table that links the named molecule to the bond entry in the Bonds table
        self.molID = self.conn.execute( """SELECT DISTINCT MOLECULE_ID FROM Molecules WHERE NAME = '""" + molname + """'""" )
        self.bondID = self.conn.execute( """SELECT DISTINCT BOND_ID FROM Bonds WHERE A1 = '""" + str(self.bond.bond.a1) + """' AND A2 = """ + str(self.bond.bond.a2) + """ AND EPAIRS = """ + str(self.bond.bond.epairs) )
        
        # Gets rid of the extra comma in the fetched data
        self.bondData = [self.molID.fetchone(), self.bondID.fetchone()]
        self.bondData = [self.bondData[0][0], self.bondData[1][0]]

        self.__setitem__('MoleculeBond', self.bondData)

    # This method adds molecule data into the Molecules table and goes to the other add methods
    def add_molecule( self, name, fp ):
        # Creates a Molecule object
        self.molecule = MolDisplay.Molecule()

        # Parse the given file
        self.molecule.parse(fp)

        # Add an entry to the Molecules table
        self.__setitem__('Molecules', name)

        # Call add_atom / add_bond for each get_ method of the molecule
        for i in range (self.molecule.atom_no):
            self.add_atom( name, self.molecule.get_atom(i) )

        for i in range (self.molecule.bond_no):
            self.add_bond( name, self.molecule.get_bond(i) )

    # This method loads molecule (atoms+bonds) data into a MolDisplay.Molecule() object
    def load_mol( self, name ):
        # Initialize the molecule object
        self.loadedMol = MolDisplay.Molecule()

        # Retrieve all of the named molecule's atoms from the database
        # Molecules name -> MoleculeAtom from MOLECULE_ID to ATOM_ID -> Atoms data
        self.appendMol = self.conn.execute( """SELECT DISTINCT Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z 
                                                FROM Molecules 
                                                INNER JOIN MoleculeAtom 
                                                ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                                                INNER JOIN Atoms
                                                ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
                                                WHERE NAME = '""" + name + """' ORDER BY Atoms.ATOM_ID;""" ).fetchall()

        # Append atom's database info to the molecule in order of increasing ATOM_ID
        for i in range (len(self.appendMol)):
            self.loadedMol.append_atom(self.appendMol[i][0], self.appendMol[i][1], self.appendMol[i][2], self.appendMol[i][3])
        
        # Retrieve all of the named molecule's bonds from the database
        # Molecules name -> MoleculeBond from MOLECULE_ID to BOND_ID -> Bonds data
        self.appendMol = self.conn.execute( """SELECT DISTINCT Bonds.A1, Bonds.A2, Bonds.EPAIRS 
                                                FROM Molecules 
                                                INNER JOIN MoleculeBond
                                                ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                                                INNER JOIN Bonds
                                                ON Bonds.BOND_ID = MoleculeBond.BOND_ID
                                                WHERE NAME = '""" + name + """' ORDER BY Bonds.BOND_ID;""" ).fetchall()

        # Append bond's database info to the molecule in order of increasing BOND_ID
        for i in range (len(self.appendMol)):
            self.loadedMol.append_bond(self.appendMol[i][0], self.appendMol[i][1], self.appendMol[i][2])

        # Returns the MolDisplay.Molecule object
        return self.loadedMol

    # This method creates a radius dictionary by using the data in the Elements table
    def radius( self ):
        # Initialize the dictionary
        self.dictionary = {}

        # Puts ELEMENT_CODE & RADIUS into a list
        self.dictionaryData = self.conn.execute( """SELECT ELEMENT_CODE, RADIUS FROM Elements ORDER BY ELEMENT_NO""" ).fetchall()

        # Gets the number of rows in ELEMENT_CODE & RADIUS
        self.dictionaryNum = self.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()
        self.dictionaryNum = self.dictionaryNum[0]

        # Create a dictionary using the data found
        for i in range(self.dictionaryNum):
            self.dictionary[self.dictionaryData[i][0]] = self.dictionaryData[i][1]

        # Return the dictionary (element code : radius)
        return self.dictionary

    # This method creates an element_name dictionary by using the data in the Elements table
    def element_name( self ):
        # Initialize the dictionary
        self.dictionary = {}

        # Puts ELEMENT_CODE & ELEMENT_NAME into a list
        self.dictionaryData = self.conn.execute( """SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements ORDER BY ELEMENT_NO""" ).fetchall()

        # Gets the number of rows in ELEMENT_CODE & ELEMENT_NAME
        self.dictionaryNum = self.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()
        self.dictionaryNum = self.dictionaryNum[0]

        # Create a dictionary using the data found
        for i in range(self.dictionaryNum):
            self.dictionary[self.dictionaryData[i][0]] = self.dictionaryData[i][1]

        # Return the dictionary (element code : element name)
        return self.dictionary

    # This method creates and returns the SVG radial gradient
    def radial_gradients( self ):
        # Initialize the final string
        self.radialGradientSVG = ""

        # Initialize the data needed to fill the SVG
        self.gradient = self.conn.execute( """SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements ORDER BY ELEMENT_NO""" ).fetchall()
        self.size = self.conn.execute( """SELECT COUNT(ELEMENT_NAME) FROM Elements""" ).fetchone()
        self.size = self.size[0]

        # Initialize the SVG
        for i in range (self.size):
            self.radialGradientSVG += """
                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                    <stop offset="0%%" stop-color="#%s"/>
                    <stop offset="50%%" stop-color="#%s"/>
                    <stop offset="100%%" stop-color="#%s"/>
                </radialGradient>""" % ( self.gradient[i][0], self.gradient[i][1], self.gradient[i][2], self.gradient[i][3] )

        return self.radialGradientSVG