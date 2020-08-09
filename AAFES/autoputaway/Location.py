import math
from prettytable import *

class Warehouse:
    def __init__(self, name, *locations):
        self.name = name
        self.locations = []
        
        for location in locations:
            self.locations.append(location)
    
    def getLocations(self):
        return self.locations

class Location:
    def __init__(self, name, height):
        self.name = name
        self.max_height = height
        self.loads = []
        self.location_crc = None
        self.status = "Empty"
        self.number_of_cases = 0
        
    def getLocationName(self):
        return self.name
    
    def getHeight(self):
        return self.max_height
    
    def getLoads(self):
        return self.loads
    
    def getLocationCRC(self):
        return self.location_crc
    
    def setLocationCRC(self, crc):
        self.location_crc = crc
    
    def getStatus(self):
        return self.status
    
    def setStatus(self, status):
        self.status = status
        
    def getCaseCount(self):
        return self.number_of_cases
    
    def setCaseCount(self, no_of_cases):
        self.number_of_cases = no_of_cases
        
    def __str__(self):
        return self.name
    
class Load:
    def __init__(self, number, product, amount):
        self.load_number = number
        self.product = product
        self.no_of_cases = amount
        self.location = None
        
    def getLoadNumber(self):
        return self.load_number
        
    def getProduct(self):
        return self.product
    
    def getCaseCount(self):
        return self.no_of_cases
    
    def setCaseCount(self, count):
        self.no_of_cases = count
        
    def getLoadLocation(self):
        return self.location
    
    def setLoadLocation(self, location):
        self.location = location
        
class Product:
    def __init__(self, name, crc, per_layer, height):
        self.name = name
        self.crc = crc
        self.cases_per_layer = per_layer
        self.case_height = height
        
    def getProductName(self):
        return self.name
    
    def getCRC(self):
        return self.crc
    
    def getCasesPerLayer(self):
        return self.cases_per_layer
    
    # The height of a case is also the height of a layer
    def getCaseHeight(self):
        return self.case_height

class JDA:
    
    # This method will be used when the application starts reading data from a database
    @staticmethod
    def prepareLoad(product, case_amount):
        pallet = Load(product, case_amount)
        return pallet
    
    #This method will only look for locations that are "Not full" or "Empty"
    #Returns: No location found or an appropriate location for the merch
    @staticmethod
    def find_eligible_location(warehouse, pallet):
        for location in warehouse.getLocations():
            if (location.status == "Not Full" and 
            pallet.getProduct().getCRC() == location.getLocationCRC()):
                return location
        
        for location in warehouse.getLocations():
            if location.getStatus() == "Empty":
                return location
            
    #Returns: Eligible or Ineligible
    @staticmethod
    def evaluate_potential_status(location, pallet):
        case_height = pallet.getProduct().getCaseHeight()
        cases_per_layer = pallet.getProduct().getCasesPerLayer()
        current_case_count = 0
        
        for load in location.getLoads():
            current_case_count += load.getCaseCount()
        
        total_cases = current_case_count + pallet.getCaseCount()
        no_of_layers =  math.ceil((total_cases / cases_per_layer))
        potential_height = no_of_layers * case_height
        
        if potential_height > location.getHeight():
            return "Ineligible"
        elif potential_height == location.getHeight():
            return "Eligible_Full"
        else:
            return "Eligible"
        
    # Also write code to tell JDA to set the status to "full"
    # If the maximum height has been reached exactly
    # We have to add the location attribute to each load. How else are we supposed to track the allocation of each load
    # Returns: success or failure
    @staticmethod
    def addLoad(warehouse, pallet):
        for location in warehouse.getLocations():
            if location.getStatus() == "Empty":
                if JDA().evaluate_potential_status(location, pallet) == "Eligible_Full":
                    location.getLoads().append(pallet)
                    pallet.setLoadLocation(location.getLocationName())
                    location.setLocationCRC(pallet.getProduct().getCRC())
                    location.setStatus("Full")
                elif JDA().evaluate_potential_status(location, pallet) == "Eligible":
                    location.getLoads().append(pallet)
                    pallet.setLoadLocation(location.getLocationName())
                    location.setLocationCRC(pallet.getProduct().getCRC())
                    location.setStatus("Not Full")
                else:
                    continue
            
            if location.getStatus() == "Not Full" and location.getLocationCRC() == pallet.getProduct().getCRC():
                if JDA().evaluate_potential_status(location, pallet) == "Eligible_Full":
                    location.getLoads().append(pallet)
                    pallet.setLoadLocation(location.getLocationName())
                    location.setStatus("Full")
                elif JDA().evaluate_potential_status(location, pallet) == "Eligible":
                    location.getLoads().append(pallet)
                    pallet.setLoadLocation(location.getLocationName())
        
        
    # This method must be run after any load is added to a location        
    @staticmethod
    def calculateNumberOfCases(location):
        case_count = 0
        
        for load in location.getLoads():
            case_count += load.getCaseCount()
        
        location.setCaseCount(case_count)
    
    # Prints all the locations in a warehouse, the products contained in them, their CRCs and number of cases
    # Returns a list of lists showing each location's Product name, CRC, Number of cases in the location and the location status
    @staticmethod
    def warehouseLocationSummary(warehouse):
        output_list = []
        
        for location in warehouse.getLocations():
            location_summary = []
            
            # Remember this is just one location. It could be empty and in such a case, write code to show that
            # it is empty. Remember: Reader friendly output
            if location.getStatus() == "Empty":
                location_summary = [location.getLocationName(), "No products", "", "0", location.getStatus()]
            else:
                location_summary.append(location.getLocationName())
                location_summary.append((location.getLoads()[0]).getProduct().getProductName())
                location_summary.append(location.getLocationCRC())
                location_summary.append(str(location.getCaseCount()))
                location_summary.append(location.getStatus())
            
            output_list.append(location_summary)
        
        return output_list

# defining the products. later versions will use a database
p1 = Product("Coca-Cola 12oz", "7381338", 20, 8)
p2 = Product("Jack Daniels", "4312481", 13, 40)
p3 = Product("Disarnonno", "1241217", 13, 20)
p4 = Product("Grey Goose", "4112462", 25, 50)
p5 = Product("Crown Royal", "8394291", 8, 25)

# defining the loads. These are the loads that will be placed in the location initially
# More will be added to test the functionality of the program
l1 = Load("2000012010", p1, 500)
l2 = Load("2000012011", p2, 100)
l3 = Load("2000012012", p3, 80)
l4 = Load("2000012013", p4, 120)
l5 = Load("2000012014", p5, 70)

# Defining the locations
loc1 = Location("Bulk 1", 300)
loc2 = Location("Bulk 2", 350)
loc3 = Location("Rack 1", 80)
loc4 = Location("Rack 2", 100)
loc5 = Location("Bulk 3", 270)
loc6 = Location("Rack 3", 100)
loc7 = Location("Rack 4", 40)

# The sole warehouse object
wh = Warehouse("WH_A", loc1, loc2, loc3, loc4, loc5, loc6, loc7)

# Used only to test the evaluate_potntial_status method
# status = JDA().evaluate_potential_status(loc7, l1)
# print(status)

# A trailer of pallets (loads) comes in from the receiving warehouse
trailer = [l1, l2, l3, l4, l5]



# We will use prettytable to format out the data at the end        
summary_list = JDA().warehouseLocationSummary(wh)
t = PrettyTable(['', 'Location', 'Product', 'CRC Number', 'Available Cases', 'Location Status'])

index = 1
for entry in summary_list:
    entry.insert(0, index)
    index += 1
    
    t.add_row(entry)

print(t)
