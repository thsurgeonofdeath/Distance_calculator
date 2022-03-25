from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom,get_ip_address
import folium
# Create your views here.

def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None
    starting = None
    
    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')

    # initial folium map
    m = folium.Map(width=800, height=500, location=[33.436117, -5.221913], zoom_start=4)

    if form.is_valid():
        instance = form.save(commit=False)
        starting_ = form.cleaned_data.get('starting')
        starting = geolocator.geocode(starting_)      
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # destination coordinates
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
        # location marker
        folium.Marker([s_lat, s_lon], tooltip='click here for more', popup=starting,
                    icon=folium.Icon(color='purple')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
                    icon=folium.Icon(color='red', icon='cloud')).add_to(m)


        # draw the line between location and destination
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