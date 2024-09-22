import tkinter as tk
from tkinter import simpledialog
from random import random
from decorator import addToObjectList

class Car:
    def __init__(self, brandName, fuelType, tankVolume):
        self.brand = brandName
        self.fuelType = fuelType
        self.tankVolume = tankVolume

        self.currentFuelVolume = round((random()+1)/4 * (tankVolume))

    def getAttributes(self):
        return self.brand, self.fuelType, self.tankVolume, self.currentFuelVolume

@addToObjectList
def createCar():
    """
    Ввод значений объекта класса Car
    """
    root = tk.Tk()
    root.withdraw()

    # Ввод значений для атрибутов
    brandName = simpledialog.askstring("Input", "Enter the brand of the car you want to add:")
    fuelType = simpledialog.askstring("Input", "Enter the fuel type this car uses")
    tankVolume = simpledialog.askinteger("Input", "Enter the volume of the car's fuel tank")

    if brandName is not None and fuelType is not None and tankVolume is not None:
        instance = Car(brandName, fuelType, tankVolume)
        print(f"Created: {instance}")
        return instance
    else:
        print("Instance creation cancelled.")
        return None

def getFunctions():
    return {"Car creator": createCar}