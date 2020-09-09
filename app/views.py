import glob
import os
from app.models import Agents_Details_Model
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.views.generic import View
import csv
from django.contrib import messages
from geopy.geocoders import Nominatim
from csv import reader
from geopy import distance
import geopy
geopy.geocoders.options.default_timeout = 7

def index(request):
    return render(request,"index.html")

class InsertData(View):
    def post(self,request):
        tsv_file=request.FILES.get("tsvfile")
        fs = FileSystemStorage()
        fs.save(tsv_file.name, tsv_file)
        newUrl = latestFile()
        if newUrl:                                      #Check for the latest file which is uploaded and insert date from the latest file
            read_tsv = csv.reader(open(newUrl), delimiter="\t")
            global counter
            counter = 0
            print("Please Wait While Agent Details Are Being Stored.")
            for row in read_tsv:
                if counter==0:
                    pass
                else:
                    try:
                        Agents_Details_Model(ID=row[0],NAME=row[1],ADDRESS=row[2],CITY=row[3],ZIPCODE=row[4],STATE=row[5]).save()
                    except:
                        pass
                counter+=1
            messages.success(request,"Agent Details Saved Successfully")
            return redirect('main')
        else:
            return redirect('main')

def latestFile():
    list_of_files = glob.glob('media/*.tsv')
    try:
        latest_file = max(list_of_files, key=os.path.getctime)              #Getting the latest file which is saved into the media directory
    except ValueError:
        latest_file=None
    return latest_file

class NearestAgent(View):
    def get(self,request):
        place=request.GET.get("ct")
        inner_place=request.GET.get("ict")
        global i_place_lat,i_place_lon,agent_lat,agent_lon,source_lat_lon,ict_bounding_box,nearest_agents,new_list3
        ict_bounding_box=[]
        geolocator = Nominatim(user_agent="app")
        location = geolocator.geocode(inner_place)              #Getting details of the place(city)
        temp=location.raw.get("boundingbox")
        ict_bounding_box=[float(x) for x in temp ]
        i_place_lat=location.latitude
        i_place_lon=location.longitude
        source_lat_lon=(i_place_lat,i_place_lon)
        print("Finding Nearest Agents. Please Wait !!")
        new_list3 = []
        try:
            with open(os.getcwd() + "/app/zipcodes/AmericaZipCodes.csv", 'r') as read_obj:  # opening Zipcode CSV File
                csv_reader = reader(read_obj)
                new_list = []
                list_of_rows = list(csv_reader)
                for data in list_of_rows:
                    if data[2] == place and data[
                        1] == inner_place:  # Finding for the State and City in AmericaZipcodeFile
                        new_list.append(data)
                    continue
                new_list2 = []

                for data2 in new_list:
                    try:
                        am = Agents_Details_Model.objects.filter(ZIPCODE=data2[
                            0])  # Filtering the Available Agents record whose zipcode matches with the AmericaZipcode Files
                        for res in am:
                            if int(data2[0]) == res.ZIPCODE:
                                new_list2.append(res)
                            else:
                                pass
                    except Agents_Details_Model.DoesNotExist:
                        pass
                for res2 in new_list2:
                    if res2 not in new_list3:
                        new_list3.append(res2)  # Filtering the duplicate records
        except FileNotFoundError:
            print("ZipCodeFile List Not Found")

        nearest_agents=[]
        if new_list3:
            for details in new_list3:  # Finding the nearest agents
                geolocator1 = Nominatim(user_agent="app")
                try:
                    agent_location = geolocator1.geocode(details.ADDRESS.rstrip('0123456789'))
                    agent_lat = agent_location.latitude
                    agent_lon = agent_location.longitude
                    dest_lat_lon = (agent_lat, agent_lon)
                    if agent_lat >= ict_bounding_box[0] and agent_lon >= ict_bounding_box[
                        2]:  # Finding the agents using boundingbox technique
                        miles = round(distance.distance(source_lat_lon, dest_lat_lon).miles, 3)
                        nearest_agents.append({"miles": miles, "details": details})
                    else:
                        pass
                except:
                    pass
            else:
                return render(request, "nearest_agent.html",
                              {"agents": nearest_agents[:100], "ct": place, "ict": inner_place})

        else:
            print("No Agnets")
            print(nearest_agents)
            return render(request,"nearest_agent.html",{"agents":[],"ct":place,"ict":inner_place})
