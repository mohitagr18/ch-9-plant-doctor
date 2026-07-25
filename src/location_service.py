# src/location_service.py

import requests
from typing import Dict, Optional
import xml.etree.ElementTree as ET
import json


class LocationService:
    """
    Service to fetch weather and soil data from zip code.
    Uses NOAA Weather API and USDA Soil Data Access (SDA).
    """
    
    def __init__(self):
        self.base_url = "https://api.weather.gov"
        self.soap_url = "https://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php"
        self.sda_url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
        self.user_agent = "AgriTech-Plant-Detector"
        self.headers = {"User-Agent": self.user_agent}
    
    def zip_to_coordinates(self, zipcode: str) -> Optional[tuple]:
        try:
            params = {'listZipCodeList': zipcode}
            response = requests.get(self.soap_url, params=params, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            lat_elem = root.find('.//latLonList')
            if lat_elem is not None and lat_elem.text:
                coords = lat_elem.text.strip().split(',')
                if len(coords) == 2:
                    return (float(coords[0]), float(coords[1]))
            return None
        except Exception as e:
            print(f"Error converting zip to coordinates: {e}")
            return None
    
    def get_weather_data(self, zipcode: str) -> Dict:
        coords = self.zip_to_coordinates(zipcode)
        if not coords:
            return {"error": f"Could not find location for zip code {zipcode}", "zipcode": zipcode}
        
        lat, lon = coords
        try:
            points_url = f"{self.base_url}/points/{lat},{lon}"
            points_data = requests.get(points_url, headers=self.headers, timeout=10).json()
            forecast_url = points_data["properties"]["forecast"]
            forecast_data = requests.get(forecast_url, headers=self.headers, timeout=10).json()
            periods = forecast_data["properties"]["periods"]
            current = periods[0] if periods else {}
            
            return {
                "zipcode": zipcode,
                "location": {
                    "latitude": lat, "longitude": lon,
                    "city": points_data["properties"]["relativeLocation"]["properties"]["city"],
                    "state": points_data["properties"]["relativeLocation"]["properties"]["state"]
                },
                "current": {
                    "temperature": current.get("temperature"),
                    "temperature_unit": current.get("temperatureUnit"),
                    "wind_speed": current.get("windSpeed"),
                    "wind_direction": current.get("windDirection"),
                    "short_forecast": current.get("shortForecast"),
                    "detailed_forecast": current.get("detailedForecast")
                },
                "forecast_3day": [
                    {"name": p.get("name"), "temperature": p.get("temperature"), "short_forecast": p.get("shortForecast")}
                    for p in periods[:6]
                ]
            }
        except Exception as e:
            return {"error": f"Failed to fetch weather data: {str(e)}", "zipcode": zipcode}
    
    def get_soil_data(self, zipcode: str) -> Dict:
        coords = self.zip_to_coordinates(zipcode)
        if not coords:
            return {"error": f"Could not find location for zip code {zipcode}", "zipcode": zipcode}
        
        lat, lon = coords
        try:
            sql_query = f"""
            SELECT TOP 1
                mu.muname AS soil_name, mu.musym AS soil_symbol,
                c.compname AS component_name, c.taxorder AS soil_order,
                c.taxsubgrp AS soil_subgroup, c.drainagecl AS drainage_class,
                ch.sandtotal_r AS sand_percent, ch.silttotal_r AS silt_percent,
                ch.claytotal_r AS clay_percent, ch.ph1to1h2o_r AS ph,
                ch.om_r AS organic_matter_percent
            FROM mapunit AS mu
            INNER JOIN component AS c ON mu.mukey = c.mukey
            INNER JOIN chorizon AS ch ON c.cokey = ch.cokey
            WHERE mu.mukey IN (
                SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('point({lon} {lat})')
            )
            AND c.comppct_r = (SELECT MAX(c2.comppct_r) FROM component AS c2 WHERE c2.mukey = mu.mukey)
            AND ch.hzdept_r = 0
            ORDER BY c.comppct_r DESC
            """
            payload = {"query": sql_query, "format": "JSON"}
            response = requests.post(self.sda_url, data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"}, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "Table" in data and len(data["Table"]) > 0:
                row = data["Table"][0]
                def safe_float(v):
                    try: return float(v) if v not in (None, "None", "") else None
                    except: return None
                
                sand = safe_float(row[6]) if len(row) > 6 else None
                silt = safe_float(row[7]) if len(row) > 7 else None
                clay = safe_float(row[8]) if len(row) > 8 else None
                ph = safe_float(row[9]) if len(row) > 9 else None
                organic_matter = safe_float(row[10]) if len(row) > 10 else None
                
                return {
                    "zipcode": zipcode,
                    "location": {"latitude": lat, "longitude": lon},
                    "soil_properties": {
                        "soil_name": row[0] or "Unknown",
                        "soil_symbol": row[1] or "Unknown",
                        "component_name": row[2] or "Unknown",
                        "soil_order": row[3] or "Unknown",
                        "soil_subgroup": row[4] or "Unknown",
                        "drainage_class": row[5] or "Unknown",
                        "sand_percent": round(sand, 1) if sand is not None else "Not available",
                        "silt_percent": round(silt, 1) if silt is not None else "Not available",
                        "clay_percent": round(clay, 1) if clay is not None else "Not available",
                        "soil_texture": self._determine_texture(clay, sand, silt),
                        "ph": round(ph, 1) if ph is not None else "Not available",
                        "organic_matter_percent": round(organic_matter, 1) if organic_matter is not None else "Not available"
                    },
                    "data_source": "USDA SSURGO via Soil Data Access"
                }
            else:
                return {
                    "zipcode": zipcode,
                    "soil_properties": {"soil_name": "No detailed soil data available for this location"},
                    "data_source": "USDA SSURGO via Soil Data Access"
                }
        except Exception as e:
            return {"error": f"Failed to fetch soil data: {str(e)}", "zipcode": zipcode}

    def _determine_texture(self, clay, sand, silt):
        try:
            clay = float(clay) if clay and clay != "None" else None
            sand = float(sand) if sand and sand != "None" else None
            silt = float(silt) if silt and silt != "None" else None
        except (ValueError, TypeError):
            return "Unknown"
        
        if not all([clay, sand, silt]):
            return "Unknown"
        
        if clay >= 40: return "Clay"
        elif clay >= 27: return "Sandy Clay" if sand > 45 else "Clay Loam"
        elif clay >= 20: return "Sandy Clay Loam" if sand > 45 else "Loam"
        elif sand >= 70: return "Sandy Clay Loam" if clay >= 15 else "Sandy Loam"
        elif silt >= 50: return "Silt Loam" if clay < 12 else "Silty Clay Loam"
        else: return "Loam"
