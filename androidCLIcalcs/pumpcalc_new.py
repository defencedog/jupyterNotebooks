#!/usr/bin/env python
# pump hand calculations
import math
import numpy as np
import warnings
import matplotlib.pyplot as plt

print ("1 - Shaft power")
print ("2 - NPSHa and Cavitation")
print ("3 - Centrifugal Pump Curve")
calc = int(input("Input 1, 2 or 3: "))
if calc==1:
	print ("Calculating shaft power")
	density=float(input("Input density of fluid in [kg/m³]: "))
	flow=float(input("Input flow of the pump [m³/h]: "))
	head=float(input("Input differental head [m]: "))
	efficiency=float(input("Input pump efficiency: "))
	rpm=float(input("Input pump speed [rpm]: "))
	power=9.81*flow*head*density/(3.6*10**6)
	shaft_power=power/efficiency
	print ("Power = %f kW" %power)
	print ("Shaft Power = %f kW" %shaft_power)
elif calc==2:
	print ("Calculating Net Positive Suction Head available - NPSHa")
	density=float(input("Input density of fluid in [kg/m³]: "))
	abs_pressure=float(input("Input absolute pressure on surface (atmospheric+gauge) [kPa A]: "))
	head_loss=float(input("Input headloss in suction pipe [m]: "))
	flow=float(input("Input flow of the pump [m³/h]: "))
	dia=float(input("Input pipe ND [mm]: "))
	vapour=float(input("Input vapour pressure of fluid [kPa]: "))
	elevation=float(input("Height of water surface ABOVE pump centre line [m]: "))
	Area=(math.pi*(dia/1000)**2)/4  #pipe area in meters
	velocity=(flow/Area)/3600 #in m/s
	NPSHa=(abs_pressure-vapour)/(9.81*density)-head_loss+elevation
	print("NPSHa= %f" %NPSHa)
	print("Note: NPSHa must be greater than NPSHr(required)")
	print("For NPSHr refer to maker's Data Sheet")
	criter=abs_pressure/(9.81*density)-vapour/(9.81*density)-head_loss-velocity**2/(2*9.81)+elevation
	if criter >0:
		print ("No cavitation in Pump Suction line - safe")
	else:
		print ("Cavitation will take place!!! Try to optimize suction line by lowering losses, increasing NB or alike") 
elif calc==3:	
	print ("Calculating Pump Curve based on minimum 3 points")
	no_pnts=int(input("Number of points to fit curve: "))
	if no_pnts < 3:
		print("Not possible to fit parabola with less than 3 points")
	else:
		flow=[]
		loss=[]
		for i in range (0, no_pnts):
			print ("Point %r" %i)
			fl=float(input("Enter flow: "))
			lo=float(input("Enter loss: "))
			Flow=flow.append(fl)
			Loss=loss.append(lo)
		warnings.simplefilter('ignore', np.RankWarning)
		coeffs=np.polyfit(flow, loss, 2)
		print(coeffs)
		print("H=%f*Q**2+%f*Q+%f" %(coeffs[0], coeffs[1], coeffs[2]))
		plt.title("Pump Headloss as function of Flow")
		plt.plot(flow, loss)
		plt.show()
		plt.savefig('xx.jpg')
else:
	print("Wrong selection")
