
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter(
    prefix="/weather",
    tags=["Weather and Irrigation"]
)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_weather(params: dict):
    """Fetch weather data from Open-Meteo."""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                WEATHER_API_URL,
                params=params
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as exc:
        print(
            f"Weather API error: {type(exc).__name__}: {exc}"
        )
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve weather data. Please try again."
        ) from exc


@router.get("/current")
async def get_current_weather(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    """Get current weather for a location."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "rain,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    data = await fetch_weather(params)

    return {
        "location": {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "timezone": data["timezone"]
        },
        "current_weather": data.get("current"),
        "units": data.get("current_units")
    }


@router.get("/forecast")
async def get_weather_forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=7)
):
    """Get a daily weather forecast."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "et0_fao_evapotranspiration"
        ),
        "forecast_days": days,
        "timezone": "auto"
    }

    data = await fetch_weather(params)

    return {
        "location": {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "timezone": data["timezone"]
        },
        "forecast": data.get("daily"),
        "units": data.get("daily_units")
    }


# ============================================================
# Phase 8.4 - Irrigation Advice
# ============================================================

class IrrigationAdviceRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    crop: str = "Rice"
    growth_stage: str = "Vegetative"

    recent_rainfall_mm: float | None = Field(
        default=None, ge=0
    )
    soil_moisture_percent: float | None = Field(
        default=None, ge=0, le=100
    )
    field_water_depth_mm: float | None = Field(
        default=None, ge=0
    )


@router.post("/irrigation-advice")
async def get_irrigation_advice(
    request: IrrigationAdviceRequest
):
    """Provide preliminary irrigation guidance for rice."""

    crop = request.crop.strip().lower()
    stage = request.growth_stage.strip().lower()

    if crop != "rice":
        raise HTTPException(
            status_code=400,
            detail="This initial irrigation rule set supports Rice only."
        )

    if stage != "vegetative":
        raise HTTPException(
            status_code=400,
            detail="This initial rule set supports the Vegetative stage only."
        )

    params = {
        "latitude": request.latitude,
        "longitude": request.longitude,
        "daily": (
            "precipitation_sum,"
            "precipitation_probability_max,"
            "et0_fao_evapotranspiration"
        ),
        "forecast_days": 3,
        "timezone": "auto"
    }

    data = await fetch_weather(params)
    forecast = data.get("daily", {})

    rainfall = forecast.get("precipitation_sum", [])
    rain_probability = forecast.get(
        "precipitation_probability_max", []
    )
    et0_values = forecast.get(
        "et0_fao_evapotranspiration", []
    )
    dates = forecast.get("time", [])

    if not rainfall or not et0_values:
        raise HTTPException(
            status_code=502,
            detail="Weather forecast is incomplete."
        )

    # Illustrative coefficient; validate locally before practical use.
    crop_coefficient = 1.05
    daily_estimates = []

    for index in range(len(rainfall)):
        et0 = (
            et0_values[index]
            if index < len(et0_values)
            else None
        )
        rain = rainfall[index]

        crop_water_demand = (
            round(et0 * crop_coefficient, 2)
            if et0 is not None
            else None
        )
        effective_rain = (
            round(rain * 0.8, 2)
            if rain is not None
            else None
        )

        daily_estimates.append({
            "date": dates[index] if index < len(dates) else None,
            "forecast_rainfall_mm": rain,
            "rain_probability_percent": (
                rain_probability[index]
                if index < len(rain_probability)
                else None
            ),
            "reference_evapotranspiration_mm": et0,
            "estimated_crop_water_demand_mm": crop_water_demand,
            "estimated_effective_rainfall_mm": effective_rain
        })

    first_rain = rainfall[0]
    first_probability = (
        rain_probability[0]
        if rain_probability
        else None
    )
    first_et0 = et0_values[0] if et0_values else None
    first_crop_demand = (
        first_et0 * crop_coefficient
        if first_et0 is not None
        else None
    )

    recommendation = (
        "Inspect the field and follow local rice water-management "
        "guidance before deciding whether to irrigate."
    )

    if (
        request.field_water_depth_mm is not None
        and request.field_water_depth_mm > 20
    ):
        recommendation = (
            "No additional irrigation is indicated by this rule "
            "right now because measured field water depth is above "
            "20 mm. Check local field-water targets and drainage."
        )

    elif (
        request.field_water_depth_mm is not None
        and request.field_water_depth_mm <= 5
    ):
        if (
            first_rain is not None
            and first_rain >= 5
            and first_probability is not None
            and first_probability >= 50
        ):
            recommendation = (
                "Field water depth is low, but meaningful rain is "
                "forecast. Recheck the field and rainfall before "
                "irrigating; do not rely on forecast probability alone."
            )
        else:
            recommendation = (
                "Measured field water depth is low. Consider "
                "irrigation according to the field's water-management "
                "method and local rice-growing guidance."
            )

    elif (
        first_rain is not None
        and first_rain >= 5
        and first_probability is not None
        and first_probability >= 50
    ):
        recommendation = (
            "Rain is forecast. Reassess field water depth after "
            "rainfall before deciding whether irrigation is needed."
        )

    elif (
        first_crop_demand is not None
        and first_rain is not None
        and first_crop_demand > first_rain
    ):
        recommendation = (
            "Estimated crop water demand exceeds forecast rainfall. "
            "Inspect field water depth and soil conditions; consider "
            "irrigation if required by your rice water-management method."
        )

    return {
        "crop": "Rice",
        "growth_stage": "Vegetative",
        "location": {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "timezone": data["timezone"]
        },
        "recommendation": recommendation,
        "input_conditions": {
            "recent_rainfall_mm": request.recent_rainfall_mm,
            "soil_moisture_percent": request.soil_moisture_percent,
            "field_water_depth_mm": request.field_water_depth_mm
        },
        "method": {
            "crop_coefficient_used": crop_coefficient,
            "note": (
                "Illustrative planning estimate: crop water demand "
                "equals reference evapotranspiration multiplied by "
                "the crop coefficient. Effective rainfall is "
                "approximated as 80% of forecast rainfall. These "
                "estimates are not a validated irrigation schedule."
            )
        },
        "three_day_estimates": daily_estimates
    }


# ============================================================
# Phase 8.5 / 8.6 - Agriculture Recommendations
# ============================================================

@router.get("/agriculture-recommendations")
async def get_agriculture_recommendations(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    crop: str = Query("Rice", min_length=2, max_length=50)
):
    """Provide preliminary weather alerts and crop-specific advice."""

    crop_name = crop.strip().lower()
    supported_crops = {
        "rice",
        "wheat",
        "tomato",
        "banana",
        "cotton",
        "maize",
        "groundnut",
        "sugarcane",
        "potato",
        "areca catechu",
        "black pepper",
    }

    if crop_name not in supported_crops:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported crop. Currently supported crops: "
                "Rice, Wheat, Tomato, Banana, Cotton, Maize, "
                "Groundnut, Sugarcane, Potato, Areca catechu, "
                "Black pepper."
            )
        )

    current_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    forecast_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "precipitation_sum,"
            "precipitation_probability_max"
        ),
        "forecast_days": 3,
        "timezone": "auto"
    }

    current_data = await fetch_weather(current_params)
    forecast_data = await fetch_weather(forecast_params)

    current = current_data.get("current", {})
    daily = forecast_data.get("daily", {})

    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind_speed = current.get("wind_speed_10m")

    max_temperatures = daily.get("temperature_2m_max", [])
    rainfall = daily.get("precipitation_sum", [])
    rain_probability = daily.get(
        "precipitation_probability_max", []
    )
    dates = daily.get("time", [])

    if (
        temperature is None
        or not max_temperatures
        or not rainfall
        or len(max_temperatures) != len(rainfall)
    ):
        raise HTTPException(
            status_code=502,
            detail="Weather forecast data is incomplete."
        )

    recommendations = []

    # These are preliminary thresholds, not crop-specific guarantees.
    if temperature >= 35:
        recommendations.append({
            "type": "heat_alert",
            "priority": "high",
            "message": (
                "High temperature detected. Monitor crops for heat "
                "stress and check soil moisture. Irrigate only when "
                "needed according to local crop guidance."
            )
        })
    elif temperature >= 30:
        recommendations.append({
            "type": "temperature",
            "priority": "medium",
            "message": (
                "Warm conditions detected. Monitor crop condition "
                "and soil moisture, especially during hot periods."
            )
        })

    if humidity is not None and humidity >= 85:
        recommendations.append({
            "type": "humidity_alert",
            "priority": "medium",
            "message": (
                "High humidity may favor some plant diseases. "
                "Inspect leaves regularly and follow crop-specific "
                "disease prevention guidance."
            )
        })

    if wind_speed is not None and wind_speed >= 30:
        recommendations.append({
            "type": "wind_alert",
            "priority": "medium",
            "message": (
                "Strong winds detected. Check local wind forecasts "
                "and protect vulnerable crops where practical."
            )
        })

    for index, rain in enumerate(rainfall):
        probability = (
            rain_probability[index]
            if index < len(rain_probability)
            else None
        )

        if (
            rain is not None
            and rain >= 10
            and probability is not None
            and probability >= 60
        ):
            recommendations.append({
                "type": "rain_alert",
                "priority": "medium",
                "date": dates[index] if index < len(dates) else None,
                "message": (
                    "Meaningful rainfall is forecast for this day. "
                    "Check drainage and reassess irrigation needs "
                    "after the rain."
                )
            })

    if not recommendations:
        recommendations.append({
            "type": "general",
            "priority": "low",
            "message": (
                "No alert was triggered by the current preliminary "
                "rules. Continue routine crop, soil-moisture and "
                "weather monitoring."
            )
        })

    crop_advice = {
        "rice": (
            "Monitor field water depth, rainfall and drainage. "
            "Follow local rice-growing water-management guidance."
            ),
        "wheat": (
            "Monitor soil moisture and temperature. Adjust irrigation "
            "to crop growth stage and local wheat-growing guidance."
            ),
        "tomato": (
            "Monitor soil moisture consistently and inspect leaves "
            "for disease symptoms, especially during humid weather."
            ),
        "banana": (
            "Monitor soil moisture regularly and maintain well-drained "
            "soil. Check for water stress during hot weather, avoid "
            "waterlogging, and inspect leaves for disease symptoms. "
            "Adjust irrigation according to the banana growth stage "
            "and local agricultural guidance."
            ),
        "cotton": (
            "Monitor soil moisture, rainfall and high temperatures. "
            "Avoid unnecessary irrigation after substantial rainfall "
            "and adjust water management to the crop growth stage."
            ),
        "maize": (
            "Monitor soil moisture and heat stress. Pay particular "
            "attention to water availability during flowering and "
            "grain formation, and account for forecast rainfall."
            ),
        "groundnut": (
            "Monitor soil moisture and ensure good drainage. Avoid "
            "waterlogging, particularly during rainy periods, and "
            "adjust irrigation to the crop growth stage."
            ),
        "sugarcane": (
            "Monitor soil moisture, temperature and rainfall. Plan "
            "irrigation according to crop growth stage and local "
            "water availability, while avoiding waterlogging."
            ),
        "potato": (
            "Monitor soil moisture and temperature carefully. Maintain "
            "relatively consistent soil moisture, ensure good drainage, "
            "and inspect foliage during humid or rainy weather."
            ),
        "areca catechu": (
            "Monitor soil moisture, rainfall and humidity. Maintain "
            "adequate moisture during dry weather, ensure drainage "
            "during heavy rain, and follow local arecanut cultivation "
            "guidance."
            ),
        "black pepper": (
            "Monitor soil moisture, rainfall and humidity. Maintain "
            "moist but well-drained soil, avoid waterlogging, and "
            "inspect vines for disease symptoms during prolonged "
            "wet or humid conditions."
            ),
        }

    recommendations.append({
        "type": "crop_specific",
        "priority": "low",
        "crop": crop_name.title(),
        "message": crop_advice[crop_name]
    })

    return {
        "success": True,
        "crop": crop_name.title(),
        "location": {
            "latitude": current_data.get("latitude"),
            "longitude": current_data.get("longitude"),
            "timezone": current_data.get("timezone")
        },
        "current_weather": {
            "temperature_celsius": temperature,
            "relative_humidity_percent": humidity,
            "wind_speed_kmh": wind_speed,
            "precipitation_mm": current.get("precipitation")
        },
        "three_day_forecast": [
            {
                "date": dates[index] if index < len(dates) else None,
                "maximum_temperature_celsius": max_temperatures[index],
                "rainfall_mm": rainfall[index],
                "rain_probability_percent": (
                    rain_probability[index]
                    if index < len(rain_probability)
                    else None
                )
            }
            for index in range(len(max_temperatures))
        ],
        "recommendations": recommendations,
        "note": (
            "Recommendations use preliminary weather thresholds. "
            "They are not a substitute for crop-specific agronomic "
            "advice or local weather warnings."
        )
    }
