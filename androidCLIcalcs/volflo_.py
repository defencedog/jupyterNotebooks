from scipy.optimize import fsolve
from math import *
import pint
unt = pint.UnitRegistry(autoconvert_offset_to_baseunit=True,\
 auto_reduce_dimensions=True)
Q_ = unt.Quantity

print ('1- Velocity [m/s] from I.D & flow')
print ('2- I.D [mm] from velocity & flow')
print ('3- Flow [m^3/hr] from I.D & velocity')

cho= int( input('Type choice 1, 2 or 3: ') )

def roots(x, *args):
	if cho==1:
		v=x
		d,f= args[0], args[1]
	elif cho==2:
		d=x
		v,f= args[0], args[1]
	else:
		f=x
		v,d= args[0], args[1]
	return f / (pi * d**2 * 0.25) - v

def caseV():
	flo= input('Type flow in m^3/hr: ')
	f= float(flo) * unt('m^3/hr')
	id= input('Type I.D in mm: ')
	d= float(id) * unt('mm')
	d.ito(unt('m'))
	sol, =fsolve( roots, x0=5000, args=(d.m,f.m) )
	sol= abs( sol.item() ) * unt('m/hr') #np.float64-> python float
	print( sol.to(unt('m/s')) ) #cannot use .ito ??

def caseD():
	flo= input('Type flow in m^3/hr: ')
	f= float(flo) * unt('m^3/hr')
	vel= input('Type velocity in m/s: ')
	v= float(vel) * unt('m/s')
	v.ito(unt('m/hr'))
	sol, =fsolve( roots, x0=0.2, args=(v.m,f.m) )
	sol= abs( sol.item() ) * unt('m')
	print( sol.to(unt('mm')) )

def caseF():
	id= input('Type I.D in mm: ')
	d= float(id) * unt('mm')
	d.ito(unt('m')) #float-> d.m is magnitude
	vel= input('Type velocity in m/s: ')
	v= float(vel) * unt('m/s')
	v.ito(unt('m/hr')) #float-> v.m is magnitude 
	sol, =fsolve( roots, x0=10, args=(v.m,d.m) )
	print( abs( sol.item() ) * unt('m^3/hr') )

caseV() if cho==1 else ( caseD() if cho==2 else caseF() )
