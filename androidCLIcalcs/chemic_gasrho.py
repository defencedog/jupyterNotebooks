import chemics as cm

formula = input("Chemical Formula e.g CH4, H3N, ClH = ")
press = float(input("Process pressure kPaA = "))
temp = float(input("Process temperature degC = "))

p = press*1000      # Absolute pressure [Pa]
tk = temp+273.15    # temperature of gas [K]

def out_():
	mw = gas.molecular_weight
	rho = gas.density()
	cp = gas.heat_capacity()
	k = gas.thermal_conductivity()
	mu = gas.viscosity() / 1000
	print(f'\n{formula} gas properties:')
	print(f'molecular weight      {mw:.2f} g/mol')
	print(f'density               {rho:.3f} kg/m³')
	print(f'heat capacity         {cp:.3f} J/(mol⋅K)')
	print(f'thermal conductivity  {k:.3f} W/(m⋅K)')
	print(f'viscosity             {mu:.3f} cP')
	print('Note: in SI units 1 cP = 10⁻³ Pa⋅s = 1 mPa⋅s')

try:
	gas = cm.Gas(formula, tk, p)
	out_()
except Exception as error:
	print(f'\n{error}')
	try:
		import cirpy as cir
		name = input('Write gas full-name = ')
		cas_ = cir.resolve(name, 'cas')
		if type(cas_)==list: # multiple cas retrieved
				print('Possible CAS:', *cas_, sep='\n- ')
				cas_f = input("Write proper CAS = ")
		else:
				print(f'\nPossible CAS: {cas_}')
				cas_f = cas_
		gas = cm.Gas(formula, tk, p, cas_number=cas_f)
		out_()
	except Exception as error:
		print(f'\n{error}')
'''
		while True:
			tmp = input('Try again? y or n = ')
			cas_f = input('Write proper CAS = ')
			gas = cm.Gas(formula, tk, p, cas_number=cas_f)
			out_()
			if tmp=='n':
				break
'''
