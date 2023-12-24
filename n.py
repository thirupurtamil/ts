from a import *
from b import *
from c import *




print("NSE Object:", nse_obj)
rajq= (get_rows)
print (rajq)







print("|-------------------------------------------------------|")
print("|{:<9}| {:<15}| {:<15}| {:<10}|".format(" Time"," Total Call OI"," Total Put OI","Trend"))

print("|-------------------------------------------------------|")
while True:
    data = importdata()
    print("|{:<9}|    {:<12}|    {:<12}| {:<10}|".format(data["Time"],data["COI"],data["POI"],data["Trend"]))
    print("|-------------------------------------------------------|")
    break 