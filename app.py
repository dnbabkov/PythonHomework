import tkinter as tk
from decorator import setApp
from tkinter import simpledialog, messagebox, ttk
import importlib
import os
import sys

class GasStation:

    def __init__(self):
        self.fuelsAndAmounts = {"Diesel": 100, "OC92": 100, "OC95": 100, "OC98": 100, "OC100": 50, "Blood": 10}
        self.queue = []

    def refuel(self):
        print(self.queue)
        if len(self.queue) != 0:
            amount = simpledialog.askinteger("Input", "Enter amount to refuel")
            if amount is None:
                messagebox.showerror("Error", "No amount given")
                return
            
            car = self.queue.pop(0)
            if car.fuelType in self.fuelsAndAmounts:
                if amount <= car.tankVolume - car.currentFuelVolume:
                    if amount <= self.fuelsAndAmounts[car.fuelType]:
                        self.fuelsAndAmounts[car.fuelType] -= amount
                        car.currentFuelVolume += amount
                        app.addObject(car)
                    else:
                        car.fillTheTank(self.fuelsAndAmounts[car.fuelType])
                        self.fuelsAndAmounts[car.fuelType] = 0
                        app.addObject(car)
                else:
                    amount = car.tankVolume - car.currentFuelVolume
                if amount <= self.fuelsAndAmounts[car.fuelType]:
                    self.fuelsAndAmounts[car.fuelType] -= amount
                    car.currentFuelVolume += amount
                    app.addObject(car)
                else:
                    car.currentFuelVolume += self.fuelsAndAmounts[car.fuelType]
                    self.fuelsAndAmounts[car.fuelType] = 0
                    app.addObject(car)
            else:
                messagebox.showerror("Error", "No such fuel")
                app.addObject(car)
                return
            self.displayData(self.frame)
        else:
            messagebox.showerror("Error", "No cars to refuel")
            return

    def refill(self):
        fuelType = simpledialog.askstring("Input", "Enter fuel type to refill")
        amount = simpledialog.askinteger("Input", "Enter amount to refill")
        if fuelType in self.fuelsAndAmounts:
            self.fuelsAndAmounts[fuelType] += amount
        self.displayData(self.frame)

    def displayData(self, frame):
        """
        Отображает данные из словаря fuelsAndAmounts.
        """

        self.frame = frame

        for widget in frame.winfo_children():
            widget.destroy()  # Очистка предыдущих виджетов

        for fuel_type, amount in self.fuelsAndAmounts.items():
            text = f"{fuel_type}: {amount} liters"
            label = tk.Label(frame, text=text)
            label.pack(anchor="w", padx=5, pady=2)

        button = tk.Button(frame, text="Refuel the car", command=self.refuel)
        button.pack(pady=10, padx=10)

        button2 = tk.Button(frame, text="Refill the station", command=self.refill)
        button2.pack(pady=10, padx=10)

    def addToQueue(self, objectList):

        if len(objectList) == 0:
            messagebox.showerror("Error", "No vehicles to add")
            return 

        selectWindow = tk.Toplevel()
        selectWindow.title = "Select vehicle to add to the queue"

        tk.Label(selectWindow, text="Select an object to add to the queue:").pack(pady=5)

        listBox = tk.Listbox(selectWindow, selectmode=tk.SINGLE)
        
        for index, obj in enumerate(objectList):
            if not objectList:
                messagebox.showerror("Error", "No available objects to add.")
                return

            for index, obj in enumerate(objectList):
                name, fuelType, tankVolume, currentFuelVolume = obj.getAttributes()
                obj_text = f"{index + 1}: {name}, {fuelType}, {currentFuelVolume}/{tankVolume}"
                listBox.insert(tk.END, obj_text)
            listBox.pack(pady=5)

            def on_select():
                selectedIndex = listBox.curselection()
                if selectedIndex:
                    selectedObject = objectList.pop(selectedIndex[0])
                    self.queue.append(selectedObject)
                    print(f"Added to queue: {selectedObject}")
                    selectWindow.destroy()

                for widget in app.upperPanel.winfo_children():
                    widget.destroy()

                for object in app.objects_list:
                    name, fuelType, tankVolume, currentFuelVolume = object.getAttributes()
                    text = f"Brand name: {name}, fuel type: {fuelType}, current fuel: {currentFuelVolume}/{tankVolume}"
                    label = tk.Label(app.upperPanel, text = text)
                    label.pack(anchor="w", padx=5, pady=2)

            addButton = tk.Button(selectWindow, text="Add to Queue", command=on_select)
            addButton.pack(pady=5)

            selectWindow.transient() 
            selectWindow.grab_set()
            selectWindow.wait_window()



class PluginApp:

    gasStations = []

    def __init__(self, root):
        self.root = root
        self.root.title("Gas Station")
        self.divisions = 1
        self.plugins = self.loadPlugins()
        self.createLayout()
        self.objects_list = []

        setApp(self)

    def loadPlugins(self):
        """
        Загрузка плагинов из директории plugins и возвращение словаря с функциями.
        """
        plugins = {}
        pluginFolder = "plugins"
        for filename in os.listdir(pluginFolder):
            if filename.endswith(".py"):
                moduleName = filename[:-3]
                modulePath = f"{pluginFolder}.{moduleName}"
                try:
                    module = importlib.import_module(modulePath)
                    if hasattr(module, "getFunctions"):
                        plugin_functions = module.getFunctions()
                        plugins[moduleName] = plugin_functions
                except Exception as e:
                    print(f"Failed to load plugin {moduleName}: {e}")
        return plugins

    def createLayout(self):
        """
        Создает основное окно.
        """
        # Панель с функциями плагинов
        self.leftPanel = tk.Frame(self.root, width=200, borderwidth=2, relief="solid")
        self.leftPanel.pack(side="left", fill="y")
        tk.Label(self.leftPanel, text="Actions", font=("Arial", 12)).pack(pady=10)

        # Панель со станциями
        self.rightPanel = tk.Frame(self.root)
        self.rightPanel.pack(side="right", fill="both", expand=True)

        # Создание панели с имеющимися объектами
        self.upperPanel = tk.Frame(self.root, height= 200, borderwidth=2, relief="solid")
        self.upperPanel.pack(side="top", fill="x")

        # Количество колонок
        self.divisions = simpledialog.askinteger("Input", "Enter a number of stations (from 1 to 5):", minvalue=1, maxvalue=5)
        if self.divisions is None:
            self.root.destroy()
            return

        # Создание кнопки для функций плагинов
        self.createPluginButtons()

        # Создание колонок
        self.createStations(self.divisions)


    def addObject(self, obj):
        """
        Метод для добавления объекта в список объектов.
        """
        if obj is not None:
            self.objects_list.append(obj)
            print(f"Object added: {obj}")

        for widget in self.upperPanel.winfo_children():
            widget.destroy()  

        for object in self.objects_list:
            name, fuelType, tankVolume, currentFuelVolume = object.getAttributes()
            text = f"Brand name: {name}, fuel type: {fuelType}, current fuel: {currentFuelVolume}/{tankVolume}"
            label = tk.Label(self.upperPanel, text = text)
            label.pack(anchor="w", padx=5, pady=2)

    def createPluginButtons(self):
        """
        Создание кнопки для каждой функции из загруженных плагинов.
        """
        for plugin_name, functions in self.plugins.items():
            tk.Label(self.leftPanel, text=plugin_name, font=("Arial", 12, "bold")).pack(pady=5)
            for function_name, function in functions.items():
                button = tk.Button(self.leftPanel, text=function_name, command=function)
                button.pack(fill="x", padx=10, pady=2)        

    def createStations(self, divisions):
        """
        Разделение на колонки
        """
        for widget in self.rightPanel.winfo_children():
            widget.destroy()

        if divisions < 1 or divisions > 5:
            messagebox.showerror("Error", "Invalid number of stations!")
            return
        
        for i in range(divisions):
            self.gasStations.append([])
            self.gasStations[i] = GasStation()

            frame = tk.Frame(self.rightPanel, borderwidth=2, relief="solid", width = 500)
            frame.grid(row=0, column=i, sticky="nsew")
            self.rightPanel.rowconfigure(i, weight=1)
            self.rightPanel.columnconfigure(i, weight=1)

            topPanel = tk.Frame(frame, bg="lightgray", height=30)
            topPanel.pack(side="top", fill="x")
            bottomPanel = tk.Frame(frame,height=30)
            bottomPanel.pack(side="bottom",fill="x")

            button = tk.Button(bottomPanel, text="Add a vehicle to the queue", 
                               command=lambda i = i: self.gasStations[i].addToQueue(self.objects_list))
            button.pack(padx=5, pady=5)

            label = tk.Label(topPanel, text=f"Station {i+1}", bg="lightgray")
            label.pack()

            content = tk.Frame(frame)
            content.pack(expand=True, fill="both")

            self.gasStations[i].displayData(content)
            

    def on_close(self):
        self.root.destroy()
        sys.exit()  # Завершение программы

if __name__ == "__main__":
    root = tk.Tk()
    global app 
    app = PluginApp(root)
    root.mainloop()
