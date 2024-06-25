# Student Name: Jessica Nguyen
# Student ID: 1169812
# Due Date: April 5th, 2023 
# Course: CIS*2750 

# localhost:59812/home_page.html, export LD_LIBRARY_PATH=`pwd`
# Warning: ELEMENT_NO number randomizer is in a range of 1-1000, File is checked when empty, but if there are newlines...
# Before turning it in: comment out all print(), database is deleted and reset = false

import sys , molsql , urllib
import random, MolDisplay, os # For random number, MolDisplay methods, and to check if it's empty
from http.server import HTTPServer, BaseHTTPRequestHandler

# list of files that we allow the web-server to serve to clients (don't serve any file that the client requests)
public_files = [ '/home_page.html', '/addremove_page.html', '/upload_page.html', '/select_page.html', '/display_page.html', '/style.css', '/script.js' ]

# Default colours & sizes (colour dictionary currently not in use)
radius = { 1: 25,
           2: 40,
         }

colour = { 1: 'ff0000',
           2: 'ff7300',
           3: 'eeff00',
           4: '00ffa2',
           5: '00aeff',
           6: '3700ff',
           7: '8c00ff',
           8: 'ff00f2',
           9: '7d7d7d',
           10: '313131',
         }

# Initialize a database
db = molsql.Database(reset=False)
db.create_tables()

class MyHandler( BaseHTTPRequestHandler ):
    # A web-form when the path is a valid file
    def do_GET(self):
        # Redirects the server if needed
        if self.path == "/":
            self.path = "/home_page.html"

        # Used to GET a file from the list of public_files, given above
        if self.path in public_files:
            self.send_response( 200 ) # OK
            if (self.path == '/style.css'):
                self.send_header( "Content-type", "text/css" )
            else:
                self.send_header( "Content-type", "text/html" )
            
            # [1:] removes the leading "/" so that the file can be found in the current dir
            fp = open( self.path[1:] )

            # load the specified file
            page = fp.read()
            fp.close()

            # create and send headers
            self.send_header( "Content-length", len(page) )
            self.end_headers()

            # Outputs the uploading option to the ported server
            self.wfile.write( bytes( page, "utf-8" ) )
        else:
            # Generates a 404 error message otherwise if it's not a public file
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: page cannot be found", "utf-8" ) )

    # A web-form when the path, “ /[FILENAME].html ” is requested (by script.js)
    def do_POST( self ):
        # Reloads the element(s) in the select list for "/add_element.html"
        if self.path == "/reload_elements.html":
            # Reload database information
            selectElementName = db.conn.execute( """SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements""" ).fetchall()
            selectElementNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()

            # Return it as a message
            if selectElementNum[0] == 0:
                message = "Invalid"
            else:
                message = ""
                for i in range(selectElementNum[0]):
                    message += selectElementName[i][1] + " (" + selectElementName[i][0] + ") "

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )

        # Reloads the molecule(s) in the select list for "/select_page.html"
        elif self.path == "/reload_molecules.html":
            # Reload database information
            selectMoleculeName = db.conn.execute( """SELECT NAME FROM Molecules""" ).fetchall()
            selectMoleculeNum = db.conn.execute( """SELECT COUNT(NAME) FROM Molecules""" ).fetchone()
        
            # Return it as a message
            if selectMoleculeNum[0] == 0:
                message = "Invalid"
            else:
                message = ""
                for i in range(selectMoleculeNum[0]):
                    if i == selectMoleculeNum[0]-1:
                        message += selectMoleculeName[i][0]
                    else:
                        message += selectMoleculeName[i][0] + " "

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )
            
        # Adds an element to the database
        elif self.path == "/add_element.html":
            # Re-initialize variable
            valid = 0

            # Convert POST content into a dictionary
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            # Gets rid of "['']" in the dictionary
            for key in postvars:
                postvalue = postvars[key]
                postvars[key] = postvalue[0] 

            # Do dummyproofing, any error = invalid input
            if "elementNum" in postvars and "elementCode" in postvars and "elementName" in postvars and "colourOne" in postvars and "colourTwo" in postvars and "colourThree" in postvars and "radius" in postvars:
                if postvars["elementNum"].isnumeric():
                    if postvars["elementCode"].isalpha() and len(postvars["elementCode"]) > 0 and len(postvars["elementCode"]) < 3:
                        if ' ' in postvars["elementCode"]:
                            valid = 0
                        else: 
                            if postvars["elementName"].isalpha() and len(postvars["elementName"]) > 2:
                                if ' ' in postvars["elementName"]:
                                    valid = 0
                                else:
                                    if len(postvars["colourOne"]) == 6 and len(postvars["colourTwo"]) == 6 and len(postvars["colourThree"]) == 6:
                                        if postvars["radius"].isnumeric():
                                            if int(postvars["radius"]) > 19 and int(postvars["radius"]) < 46:
                                                valid = 1

            # If all inputs are valid
            if valid == 1:
                # Check if it exists in the database
                existingData = db.conn.execute( """SELECT ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS FROM Elements ORDER BY ELEMENT_NO""" ).fetchall()
                existingDataNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()

                for i in range(existingDataNum[0]):
                    # Required invalidations (has to be unique):
                    if existingData[i][1] == postvars["elementCode"]:
                        valid = 2
                        break
                    if int(existingData[i][0]) == int((postvars["elementNum"])):
                        valid = 3
                        break

                    # Optional invalidations I've created
                    if existingData[i][2] == postvars["elementName"]:
                        valid = 4
                        break
                    #if existingData[i][3] == postvars["colourOne"] and existingData[i][4] == postvars["colourTwo"] and existingData[i][5] == postvars["colourThree"] and int(existingData[i][6]) == int(postvars["radius"]):
                    #    valid = 5
                    #    break

                # Add the inputted element into the database if its unique
                if valid == 2:
                    message = "Invalid input: element code is taken."
                elif valid == 3:
                    message = "Invalid input: element number is taken."
                elif valid == 4:
                    message = "Invalid input: element name is taken."
                #elif valid == 5:
                #    message = "Invalid input: element colour x size combination already exists."
                else:
                    data = [postvars["elementNum"], postvars["elementCode"], postvars["elementName"], postvars["colourOne"], postvars["colourTwo"], postvars["colourThree"], postvars["radius"]]
                    db.__setitem__( 'Elements', data )
                    message = str(postvars["elementName"]) + " has been saved."
                
                #print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() )

            else:
                message = "Invalid input: missing required input(s)."

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )

        # Removes an element from the database
        elif self.path == "/remove_element.html":
            # Convert POST content into a dictionary
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            # Gets rid of "['']" in the dictionary
            postvalue = postvars["selectElement"]

            # Delete element
            message = "deleted."
            postvalue = postvalue[0].split()
            if len(postvalue[1]) == 3:
                db.conn.execute( """DELETE FROM Elements WHERE ELEMENT_CODE = '""" + postvalue[1][1] + """'""" )
            else:
                db.conn.execute( """DELETE FROM Elements WHERE ELEMENT_CODE = '""" + postvalue[1][1] + postvalue[1][2] + """'""" )

            #print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() )

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )
            
        # Uploads a molecule into the database
        elif self.path == "/upload_molecule.html":
            # Re-initialize variable
            valid = 0

            # Convert POST content into a dictionary
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            # Gets rid of "['']" in the dictionary
            for key in postvars:
                postvalue = postvars[key]
                postvars[key] = postvalue[0]

            # Checks if anything was inputted and if the upload is an SDF
            if "molUpload" in postvars and "molName" in postvars:
                postvars["molUpload"] = postvars["molUpload"][12:]
                size = os.path.getsize(postvars["molUpload"])
                if size == 0:
                    message = "Invalid Input: uploaded file is empty."
                elif ' ' in postvars["molName"]:
                    message = "Invalid Input: no spaces allowed in molecule name."
                elif ".sdf" in postvars["molUpload"]:
                    # Checks that the molecule name is not already in use
                    existingData = db.conn.execute( """SELECT NAME FROM Molecules""" ).fetchall()
                    existingDataNum = db.conn.execute( """SELECT COUNT(NAME) FROM Molecules""" ).fetchone()

                    for i in range(existingDataNum[0]):
                        if existingData[i][0] == postvars["molName"]:
                            valid = 1
                            break

                    if valid == 1:
                        message = "Invalid input: molecule name is taken."
                    else:
                        # Opens the file to see if it exists
                        try:
                            fp = open(postvars["molUpload"])
                        except FileNotFoundError:
                            valid = 2
                        
                        # Add it to the database if it's valid
                        if valid == 2:
                            message = "Invalid input: SDF file does not exist."
                        else:
                            try:
                                db.add_molecule(postvars["molName"], fp)
                                message = str(postvars["molName"]) + " has been added."

                                # Obtain number of atoms in the molecule
                                fp = open(postvars["molUpload"])
                                multipleLines = fp.readlines()        
                                fp.close()
                                line = multipleLines.pop(0)
                                line = multipleLines.pop(0)
                                line = multipleLines.pop(0)
                                line = multipleLines.pop(0).split()
                                numOfAtoms = int(line[0])

                                # Obtain database elements & count
                                dbElement = db.conn.execute( """SELECT ELEMENT_CODE, ELEMENT_NO FROM Elements""" ).fetchall()
                                dbElementNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()

                                # Add elements to the database if they're missing
                                for i in range(numOfAtoms):
                                    valid = 0
                                    line = multipleLines.pop(0).split()

                                    # Put all uploaded molecule elements into the database (as permanent elements)
                                    dbPerm = db.conn.execute( """SELECT ELEMENT_CODE FROM PermanentElements""" ).fetchall()
                                    dbPermNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM PermanentElements""" ).fetchone()
                                    if dbPermNum[0] == 0:
                                        db.conn.execute( """INSERT INTO PermanentElements ( ELEMENT_CODE ) VALUES ( ? );""", tuple([line[3]]) )
                                    else:
                                        # Add to database if it's a unique element
                                        for k in range(dbPermNum[0]):
                                            addPerm = 0
                                            if dbPerm[k][0] == [line[3]]:
                                                addPerm = 1
                                                break
                                        if addPerm == 0:
                                            db.conn.execute( """INSERT INTO PermanentElements ( ELEMENT_CODE ) VALUES ( ? );""", tuple([line[3]]) )

                                    # Check if it matches element codes in the database
                                    for j in range(dbElementNum[0]):
                                        if line[3] == dbElement[j][0]:
                                            valid = 3
                                            break
                                        
                                    # If not matching to any, add it to the Elements database
                                    if valid == 0:
                                        # Find a unique number
                                        elementNum = random.randint(1,1000)
                                        while 1:
                                            valid = 0
                                            for j in range(dbElementNum[0]):
                                                if elementNum == dbElement[j][1]:
                                                    elementNum = random.randint(1,1000)
                                                    valid = 4
                                                    break
                                            if valid == 0:
                                                break

                                        data = [elementNum, line[3], line[3], colour[random.randint(1,10)], "050505", "000000", radius[random.randint(1,2)]]
                                        db.__setitem__( 'Elements', data )

                                        # Refresh database
                                        dbElement = db.conn.execute( """SELECT ELEMENT_CODE, ELEMENT_NO FROM Elements""" ).fetchall()
                                        dbElementNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()
                            except ValueError:
                                message = "Invalid input: SDF file is improperly formatted."

                        #print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() )
                        #print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() )
                else:  
                    message = "Invalid input: file is not an SDF."
            else:
                message = "Invalid input: missing required input(s)."

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )
        
        # Finds and returns the number of atoms/bonds to display it
        elif self.path == "/select_molecule1.html":
            # Convert POST content into a dictionary
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            # Gets rid of "['']" in the dictionary
            postvalue = postvars["selected"]

            # Find the number of atoms and bonds in this molecule
            mol = db.load_mol(postvalue[0])

            # Return the number of atoms and bonds
            message = str(mol.atom_no) + " " + str(mol.bond_no)

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )

        # Selects the molecule that the user chooses
        elif self.path == "/select_molecule2.html":
            # Convert POST content into a dictionary
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            # Gets rid of "['']" in the dictionary
            postvalue = postvars["selectMolecule"]

            # Return a message
            message = str(postvalue[0]) + " has been selected."

            # Save molecule to the database
            db.conn.execute( """DELETE FROM SelectedMolecule;""" )
            db.conn.execute( """INSERT INTO SelectedMolecule ( MOLECULE_NAME ) VALUES ( ? );""", tuple([postvalue[0]]) )

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )

        # Displays appropriate message depending on if a molecule was selected for display
        elif self.path == "/display_molecule_msg.html":
            dbDisplay = db.conn.execute( """SELECT MOLECULE_NAME FROM SelectedMolecule""" ).fetchone()
            dbDisplayNum = db.conn.execute( """SELECT COUNT(MOLECULE_NAME) FROM SelectedMolecule""" ).fetchone()

            # Notifies user if finalMol should be displayed
            if dbDisplayNum[0] > 0:
                message = str(dbDisplay[0])
            else:
                message = "No molecules were selected for display."

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )

        # Displays the selected molecule by returning the SVG of it
        elif self.path == "/display_molecule_pic.html":
            dbDisplay = db.conn.execute( """SELECT MOLECULE_NAME FROM SelectedMolecule""" ).fetchone()
            dbDisplayNum = db.conn.execute( """SELECT COUNT(MOLECULE_NAME) FROM SelectedMolecule""" ).fetchone()

            if dbDisplayNum[0] > 0:
                # Add all missing molecule elements into the database 
                dbElement = db.conn.execute( """SELECT ELEMENT_CODE, ELEMENT_NO FROM Elements""" ).fetchall()
                dbElementNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()
                dbPerm = db.conn.execute( """SELECT ELEMENT_CODE FROM PermanentElements""" ).fetchall()
                dbPermNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM PermanentElements""" ).fetchone()
                
                for i in range(dbPermNum[0]):
                    valid = 0

                    for j in range(dbElementNum[0]):
                        if dbPerm[i][0] == dbElement[j][0]:
                            valid = 1
                            break

                    # If the element is not in the Elements database, add it
                    if valid == 0:
                        # Find a unique number
                        elementNum = random.randint(1,1000)
                        while 1:
                            valid = 0
                            for j in range(dbElementNum[0]):
                                if elementNum == dbElement[j][1]:
                                    elementNum = random.randint(1,1000)
                                    valid = 1
                                    break
                            if valid == 0:
                                break

                        data = [elementNum, dbPerm[i][0], dbPerm[i][0], colour[random.randint(1,10)], "050505", "000000", radius[random.randint(1,2)]]
                        db.__setitem__( 'Elements', data )

                        # Refresh database
                        dbElement = db.conn.execute( """SELECT ELEMENT_CODE, ELEMENT_NO FROM Elements""" ).fetchall()
                        dbElementNum = db.conn.execute( """SELECT COUNT(ELEMENT_CODE) FROM Elements""" ).fetchone()
                
                # Input default values
                MolDisplay.radius = db.radius()
                MolDisplay.element_name = db.element_name()
                MolDisplay.header += db.radial_gradients()

                # Obtain SVG
                mol = db.load_mol(dbDisplay[0])
                mol.sort()
                message = mol.svg()
            else:
                message = "No display."

            # Notify the user on the web page
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()
            self.wfile.write( bytes( message, "utf-8" ) )

        else:
            # Generates a 404 error message otherwise
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: page cannot be found", "utf-8" ) )

# Allows for a server/port to be created
httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler )
httpd.serve_forever()