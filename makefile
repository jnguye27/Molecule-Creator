all: libmol.so swig _molecule.so

mol.o: mol.c mol.h
	clang -Wall -std=c99 -pedantic -c mol.c -fPIC -o mol.o

libmol.so: mol.o
	clang mol.o -shared -o libmol.so

swig: molecule.i
	swig -python molecule.i

molecule_wrap.o: molecule_wrap.c
	clang -Wall -std=c99 -pedantic -fPIC -c molecule_wrap.c -I /usr/include/python3.7

_molecule.so: molecule_wrap.o
	clang molecule_wrap.o -shared -o _molecule.so -lpython3.7 -lmol -L. -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

clean:
	rm -f *.o *.so

