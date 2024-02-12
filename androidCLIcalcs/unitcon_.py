import pint
unt = pint.UnitRegistry(autoconvert_offset_to_baseunit=True, auto_reduce_dimensions=True)

print('Usage: quantity<space>fromUnit<space>toUnit', 'Type end to stop loop', sep='\n')

while True:
 tmp= input('Input quantity & units: ')
 if tmp=='end':
  break
 tmp= tmp.split()
 print( (float(tmp[0]) * unt(tmp[1])).to(unt(tmp[2])) )


