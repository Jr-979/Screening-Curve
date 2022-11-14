import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from math import e,pow
import argparse

class PowerStation:
    def __init__(self, StationName, OvernightCost,
                        FuelCost, LifeOfPlant, DiscountRate) -> None:
        self.stName = StationName
        self.OC = OvernightCost
        # M --> k hr --> yr
        self.fuel = round(FuelCost * 8.76,2)
        self.T = LifeOfPlant
        self.r = DiscountRate

        # From Fixed cost formular 
        # FC = (r * OC) / (1-1/(1+r)^T)
        self.FC = (self.r * self.OC)/(1- pow(e,(-1*(self.r*self.T))))

        # Variable cost calculated from fuel cost
        # VC = Fuel cost
        self.VC = self.fuel

        # Calculate flag
        self.isCalculated = False
        # Using memolization technique for reduced time complexity
        self._memo = {}

    def calculateARR(self,capacityFactor : float) -> float:
        # Calcuate ARR by using formular ARR = fixed cost + capacity factor * variable cost
        self._memo[capacityFactor] = self.FC + capacityFactor*self.VC

        # Set the stop iteration flag when CF = 1.0
        if capacityFactor >= 1.0: 
            self.isCalculated = True

        # Store calculated value as hash map for later use
        return self._memo[capacityFactor]

    def plot(self)-> None:
        # Plot store values
        if not self.isCalculated:
            raise ValueError("Please complete the itteration with calculateARR first")

        plt.plot(*zip(*sorted(self._memo.items())),label = self.stName)


    def __str__(self)-> str:
        return f"Station name : {self.stName}{chr(10)}Overnight Cost : {self.OC}{chr(10)}Fuel Cost : {self.fuel}{chr(10)}Life of plant : {self.T}{chr(10)}Discount rate : {self.r}"




if __name__ == "__main__" :
     # Read station data from csv 
    parser = argparse.ArgumentParser(description='Plot screening curve')
    parser.add_argument('path', metavar='path', default="",type=str,help='Path to csv file')
    args = parser.parse_args()

    if args.path == "": args.path = "new.csv"

    stations = pd.read_csv(args.path).to_dict('records')
    stations = [PowerStation(**station) for station in stations]

    step_size = 1e-5
    CF = np.arange(0,1.0+step_size,step_size).round(5).tolist()

    # Initialize space for intersetion point
    intersectionx ,intersectiony = [],[]
    pointPrev = -1

    # Iterate capacity factor value from 0 to 1.0 
    for cf in CF:
        results = []
        # Loop through every station
        for station in stations:
            results.append(station.calculateARR(capacityFactor= cf))

        # Find the lowest prices generators
        point = min(range(len(results)),key=results.__getitem__)

        # If current generator no longer the cheapest -> Intersection point occur
        if point != pointPrev:
            if cf != 0.0:
                intersectionx.append(cf)
                intersectiony.append(min(results))
            
        pointPrev = point

    # Show the resukt
    print("Screening Curve")
    for idx, x in enumerate(intersectionx):
        print(f"Cheapest to run when CF < {round(x,5)} : {stations[idx].stName}  : {round(x*8760,2)} hr" )
    else:
        print(f"Cheapest to run when CF > {round(intersectionx[-1],5)} : {stations[-1].stName} : {round(x*8760,2)} hr" )

    # Show the plot
    for station in stations : station.plot()
    plt.plot(intersectionx,intersectiony,marker = "o", markersize=5)
    plt.legend()
    plt.show()
