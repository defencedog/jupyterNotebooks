import chemics as cm

eq = {
			1:'NaCl + H2O -> 0.5 Cl2 + 0.5 H2 + NaOH',
			2:'Cl2 + 2 NaOH -> NaCl + NaClO + H2O',
			3:'2 HCl + CaCO3 -> CaCl2 + CO2 + H2O',
			4:'4 OH- -> 4 e- + 2 H2O + O2',
			5:'H2 + Cl2 -> 2 HCl',
			}

print('Equations in database: ')
[print(x,'] ', eq[x], sep='') for x in eq]
# get equation string from stored dict
usr = eq[ int(input('Select equation number [e.g 2]: ')) ]
# convert str to chemics obj
ce = cm.ChemicalEquation(usr)

print('\n', ce.eq)
print('Is Balance: ', ce.is_balanced())
print('Reactant Total Mass: ', round(ce.rct_mass,4))
print('Product Total Mass: ', round(ce.prod_mass,4))

print('\n', 'Reactant Table:', sep='')
print(ce.rct_properties)
print('\n', 'Product Table:', sep='')
print(ce.prod_properties)
