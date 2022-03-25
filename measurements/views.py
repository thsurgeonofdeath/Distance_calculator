from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
# Create your views here.

# function to get the center coordinates between two locations :
def get_center_coordinates(latA, longA, latB=None, longB=None):
    cord = (latA, longA)
    if latB:
        cord = [(latA+latB)/2, (longA+longB)/2]
    return cord

# function to control the zoom depending on the distance between the two cities
def get_zoom(distance):
    if distance <=100:
        return 8
    elif distance > 100 and distance <= 5000:
        return 4
    else:
        return 2

# the view of the web application :
def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None
    starting = None
    
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')

    # initial folium map
    m = folium.Map(width=800, height=500, location=[33.436117, -5.221913], zoom_start=4)

    if form.is_valid():
        instance = form.save(commit=False)
        #setting the values of the starting point and the destination obtained from the form
        starting_ = form.cleaned_data.get('starting')
        starting = geolocator.geocode(starting_)      
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # getting the starting point and  destination coordinates
        s_lat = starting.latitude
        s_lon = starting.longitude
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointA = (s_lat, s_lon)
        pointB = (d_lat, d_lon)
        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # folium map modification
        m = folium.Map(width=800, height=500, location=get_center_coordinates(s_lat, s_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        
        # starting point marker
        folium.Marker([s_lat, s_lon], tooltip='click here for more', popup=starting,
                    icon=folium.Icon(color='purple')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
                    icon=folium.Icon(color='red', icon='cloud')).add_to(m)


        # draw the line between the starting point and the destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=5, color='blue')
        m.add_child(line)
        
        instance.starting = starting
        instance.distance = distance
        instance.save()
    
    m = m._repr_html_()

    context = {
        'distance' : distance,
        'starting' : starting,
        'destination': destination,
        'form': form,
        'map': m,
    }

    return render(request, 'measurements/main.html', context)