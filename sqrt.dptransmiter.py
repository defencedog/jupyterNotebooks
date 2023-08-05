# mA output standard
x = [4, 20]
# process parameter range in kPa
y = [0, 4.9]
# range in terms of %age
z = [0, 100]
import itertools as it
import math as m
# preparing arbitrary 25 value array of process variable
# within LRV & URV instrument range
# lastly rounding-off for clean plots
y_sq= list( (it.takewhile(lambda x: x<=y[1], it.count(0,y[1]/26)) ) )
y_sq= [round (i,2) for i in y_sq]
# it generates 25 value array b/w 0 & 100%
z_sq= list( (it.takewhile(lambda x: x<=z[1], it.count(0,4)) ) )
z_sq= [round (i,2) for i in z_sq]

import matplotlib.pyplot as plt
fig = plt.figure( figsize=(5,4)  )
# creating x2 graphs vertically aligned
ax1 = plt.subplot(2, 1, 1)
ax2 = ax1.twinx()
ax3 = plt.subplot(2, 1, 2)
ax4 = ax3.twinx()
# start of 1st graph
ax1.minorticks_on()
ax1.grid(which='both')
ax1.set_xlabel('mAmpere', fontweight='bold')
ax1.set_ylabel(r'$\sqrt{kPa}$', fontweight='bold')
ax2.set_ylabel('%age', fontweight='bold')
# sqrt 4-20mA calculated correponding to process variable
# https://www.sensorsone.com/linear-measurement-to-square-root-extraction-4-20ma-converter/
ax1.plot( [4+(16*m.sqrt( (i-y[0]) / (y[1]-y[0]) )) for i in y_sq], y_sq, 'b')
ax2.plot( [4+(16*m.sqrt( (i-y[0]) / (y[1]-y[0]) )) for i in y_sq], z_sq, 'b')
# start of 2nd graph
ax3.minorticks_on()
ax3.grid(which='both')
ax3.set_xlabel('mAmpere', fontweight='bold')
ax3.set_ylabel('kPa', fontweight='bold')
ax4.set_ylabel('%age', fontweight='bold')
# simple linear transfer function of mA output
ax3.plot( x, y, 'b' )
ax4.plot( x, z, 'b' )

fig.tight_layout()
plt.savefig('3.jpg', dpi=300)
