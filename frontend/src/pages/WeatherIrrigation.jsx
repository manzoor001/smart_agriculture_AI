import { useState } from "react";
import api from "../services/api";
import "./WeatherIrrigation.css";

const initialLocation = {
  latitude: "11.0168",
  longitude: "76.9558",
};

const cropOptions = [
  "Rice",
  "Wheat",
  "Tomato",
  "Banana",
  "Cotton",
  "Maize",
  "Groundnut",
  "Sugarcane",
  "Potato",
  "Areca catechu",
  "Black pepper",
];

function displayValue(value, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  return `${value}${suffix}`;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(`${value}T00:00:00`);

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
}

function readableLabel(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function WeatherIrrigation() {
  const [location, setLocation] = useState(initialLocation);
  const [days, setDays] = useState("7");
  const [crop, setCrop] = useState("Rice");

  const [recentRainfall, setRecentRainfall] = useState("");
  const [soilMoisture, setSoilMoisture] = useState("");
  const [fieldWaterDepth, setFieldWaterDepth] = useState("");

  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [irrigationAdvice, setIrrigationAdvice] = useState(null);
  const [agricultureAdvice, setAgricultureAdvice] = useState(null);

  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  function getCoordinates() {
    const latitude = Number(location.latitude);
    const longitude = Number(location.longitude);

    if (
      location.latitude.trim() === "" ||
      location.longitude.trim() === "" ||
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      throw new Error(
        "Enter a valid latitude (-90 to 90) and longitude (-180 to 180)."
      );
    }

    return { latitude, longitude };
  }

  async function runRequest(requestName, requestFunction) {
    setLoading(requestName);
    setError("");

    try {
      await requestFunction();
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : err.message || "Unable to retrieve weather information."
      );
    } finally {
      setLoading("");
    }
  }

  async function loadCurrentWeather() {
    await runRequest("current", async () => {
      const coordinates = getCoordinates();
      const response = await api.get("/weather/current", {
        params: coordinates,
      });

      setCurrentWeather(response.data);
    });
  }

  async function loadForecast() {
    await runRequest("forecast", async () => {
      const coordinates = getCoordinates();
      const response = await api.get("/weather/forecast", {
        params: {
          ...coordinates,
          days: Number(days),
        },
      });

      setForecast(response.data);
    });
  }

  async function loadIrrigationAdvice() {
    await runRequest("irrigation", async () => {
      const coordinates = getCoordinates();

      const payload = {
        ...coordinates,
        crop: "Rice",
        growth_stage: "Vegetative",
        recent_rainfall_mm:
          recentRainfall.trim() === ""
            ? null
            : Number(recentRainfall),
        soil_moisture_percent:
          soilMoisture.trim() === ""
            ? null
            : Number(soilMoisture),
        field_water_depth_mm:
          fieldWaterDepth.trim() === ""
            ? null
            : Number(fieldWaterDepth),
      };

      if (
        (payload.recent_rainfall_mm !== null &&
          (!Number.isFinite(payload.recent_rainfall_mm) ||
            payload.recent_rainfall_mm < 0)) ||
        (payload.soil_moisture_percent !== null &&
          (!Number.isFinite(payload.soil_moisture_percent) ||
            payload.soil_moisture_percent < 0 ||
            payload.soil_moisture_percent > 100)) ||
        (payload.field_water_depth_mm !== null &&
          (!Number.isFinite(payload.field_water_depth_mm) ||
            payload.field_water_depth_mm < 0))
      ) {
        throw new Error(
          "Check your measurements. Rainfall and water depth must be non-negative; soil moisture must be 0–100%."
        );
      }

      const response = await api.post(
        "/weather/irrigation-advice",
        payload
      );

      setIrrigationAdvice(response.data);
    });
  }

  async function loadAgricultureRecommendations() {
    await runRequest("recommendations", async () => {
      const coordinates = getCoordinates();

      const response = await api.get(
        "/weather/agriculture-recommendations",
        {
          params: {
            ...coordinates,
            crop,
          },
        }
      );

      setAgricultureAdvice(response.data);
    });
  }

  const current = currentWeather?.current_weather || {};
  const currentUnits = currentWeather?.units || {};
  const dailyForecast = forecast?.forecast || {};

  const forecastDates = dailyForecast.time || [];
  const maxTemperatures = dailyForecast.temperature_2m_max || [];
  const minTemperatures = dailyForecast.temperature_2m_min || [];
  const rainAmounts = dailyForecast.precipitation_sum || [];
  const rainProbabilities =
    dailyForecast.precipitation_probability_max || [];
  const evapotranspiration =
    dailyForecast.et0_fao_evapotranspiration || [];

  return (
    <div className="weather-page">
      <div className="weather-page-header">
        <div>
          <p className="weather-eyebrow">SMART AGRICULTURE AI</p>
          <h1>Weather &amp; Irrigation</h1>
          <p className="weather-subtitle">
            Monitor weather, check upcoming rainfall and get preliminary
            crop-specific guidance.
          </p>
        </div>

        <div className="weather-header-icon" aria-hidden="true">
          🌦️
        </div>
      </div>

      <section className="weather-card location-card">
        <div className="weather-section-heading">
          <div>
            <h2>Farm Location</h2>
            <p>Enter the coordinates of your farm.</p>
          </div>
          <span className="weather-location-badge">GPS coordinates</span>
        </div>

        <div className="weather-form-grid">
          <label className="weather-field">
            <span>Latitude</span>
            <input
              type="number"
              min="-90"
              max="90"
              step="any"
              value={location.latitude}
              onChange={(event) =>
                setLocation({
                  ...location,
                  latitude: event.target.value,
                })
              }
              placeholder="Example: 11.0168"
            />
          </label>

          <label className="weather-field">
            <span>Longitude</span>
            <input
              type="number"
              min="-180"
              max="180"
              step="any"
              value={location.longitude}
              onChange={(event) =>
                setLocation({
                  ...location,
                  longitude: event.target.value,
                })
              }
              placeholder="Example: 76.9558"
            />
          </label>

          <label className="weather-field">
            <span>Forecast duration</span>
            <select
              value={days}
              onChange={(event) => setDays(event.target.value)}
            >
              {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                <option key={day} value={day}>
                  {day} {day === 1 ? "day" : "days"}
                </option>
              ))}
            </select>
          </label>
        </div>

        <p className="weather-location-help">
          The starting coordinates are for Coimbatore. Change them to your
          farm's coordinates if needed.
        </p>
      </section>

      {error && (
        <div className="weather-error" role="alert">
          <span>⚠️</span>
          <p>{error}</p>
          <button
            type="button"
            onClick={() => setError("")}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      <section className="weather-action-grid">
        <article className="weather-action-card">
          <div className="weather-action-icon">🌤️</div>
          <h3>Current Weather</h3>
          <p>View current temperature, humidity, wind and rainfall.</p>
          <button
            type="button"
            onClick={loadCurrentWeather}
            disabled={Boolean(loading)}
          >
            {loading === "current" ? "Loading..." : "Get Current Weather"}
          </button>
        </article>

        <article className="weather-action-card">
          <div className="weather-action-icon">📅</div>
          <h3>Weather Forecast</h3>
          <p>Review upcoming temperatures, rainfall and rain probability.</p>
          <button
            type="button"
            onClick={loadForecast}
            disabled={Boolean(loading)}
          >
            {loading === "forecast" ? "Loading..." : "View Forecast"}
          </button>
        </article>

        <article className="weather-action-card">
          <div className="weather-action-icon">💧</div>
          <h3>Rice Irrigation Advice</h3>
          <p>Estimate water demand and review the three-day outlook.</p>
          <button
            type="button"
            onClick={loadIrrigationAdvice}
            disabled={Boolean(loading)}
          >
            {loading === "irrigation" ? "Calculating..." : "Get Irrigation Advice"}
          </button>
        </article>

        <article className="weather-action-card">
          <div className="weather-action-icon">🌱</div>
          <h3>Crop Recommendations</h3>
          <p>Check preliminary weather alerts and crop-specific guidance.</p>
          <button
            type="button"
            onClick={loadAgricultureRecommendations}
            disabled={Boolean(loading)}
          >
            {loading === "recommendations"
              ? "Checking..."
              : "Get Recommendations"}
          </button>
        </article>
      </section>

      {currentWeather && (
        <section className="weather-card weather-results">
          <div className="weather-section-heading">
            <div>
              <h2>Current Conditions</h2>
              <p>
                {currentWeather.location?.timezone || "Local farm time"}
              </p>
            </div>
            <span className="weather-result-icon">☀️</span>
          </div>

          <div className="weather-metric-grid">
            <div className="weather-metric weather-temperature">
              <span>Temperature</span>
              <strong>
                {displayValue(
                  current.temperature_2m,
                  ` ${currentUnits.temperature_2m || "°C"}`
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Feels Like</span>
              <strong>
                {displayValue(
                  current.apparent_temperature,
                  ` ${currentUnits.apparent_temperature || "°C"}`
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Humidity</span>
              <strong>
                {displayValue(
                  current.relative_humidity_2m,
                  ` ${currentUnits.relative_humidity_2m || "%"}`
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Wind Speed</span>
              <strong>
                {displayValue(
                  current.wind_speed_10m,
                  ` ${currentUnits.wind_speed_10m || "km/h"}`
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Precipitation</span>
              <strong>
                {displayValue(
                  current.precipitation,
                  ` ${currentUnits.precipitation || "mm"}`
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Weather Code</span>
              <strong>{displayValue(current.weather_code)}</strong>
            </div>
          </div>

          <p className="weather-location-line">
            Coordinates: {currentWeather.location?.latitude},{" "}
            {currentWeather.location?.longitude}
          </p>
        </section>
      )}

      {forecast && (
        <section className="weather-card weather-results">
          <div className="weather-section-heading">
            <div>
              <h2>Daily Forecast</h2>
              <p>
                {forecastDates.length} forecast days ·{" "}
                {forecast.location?.timezone || "Local timezone"}
              </p>
            </div>
            <span className="weather-result-icon">🗓️</span>
          </div>

          <div className="weather-table-wrapper">
            <table className="weather-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Max Temp.</th>
                  <th>Min Temp.</th>
                  <th>Rainfall</th>
                  <th>Rain Chance</th>
                  <th>ET₀</th>
                </tr>
              </thead>
              <tbody>
                {forecastDates.map((date, index) => (
                  <tr key={date || index}>
                    <td>{formatDate(date)}</td>
                    <td>{displayValue(maxTemperatures[index], " °C")}</td>
                    <td>{displayValue(minTemperatures[index], " °C")}</td>
                    <td>{displayValue(rainAmounts[index], " mm")}</td>
                    <td>
                      {displayValue(rainProbabilities[index], "%")}
                    </td>
                    <td>
                      {displayValue(evapotranspiration[index], " mm")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="weather-footnote">
            ET₀ is reference evapotranspiration, not a direct measurement
            of your crop's water requirement.
          </p>
        </section>
      )}

      <section className="weather-card irrigation-input-card">
        <div className="weather-section-heading">
          <div>
            <h2>Optional Field Measurements</h2>
            <p>
              These measurements provide additional context for the rice
              irrigation rules.
            </p>
          </div>
          <span className="weather-result-icon">🌾</span>
        </div>

        <div className="weather-form-grid">
          <label className="weather-field">
            <span>Recent rainfall (mm)</span>
            <input
              type="number"
              min="0"
              step="any"
              value={recentRainfall}
              onChange={(event) => setRecentRainfall(event.target.value)}
              placeholder="Optional"
            />
          </label>

          <label className="weather-field">
            <span>Soil moisture (%)</span>
            <input
              type="number"
              min="0"
              max="100"
              step="any"
              value={soilMoisture}
              onChange={(event) => setSoilMoisture(event.target.value)}
              placeholder="Optional"
            />
          </label>

          <label className="weather-field">
            <span>Field water depth (mm)</span>
            <input
              type="number"
              min="0"
              step="any"
              value={fieldWaterDepth}
              onChange={(event) => setFieldWaterDepth(event.target.value)}
              placeholder="Optional"
            />
          </label>
        </div>

        <p className="weather-location-help">
          Leave a measurement blank if you do not know it. Soil moisture
          and recent rainfall are currently recorded as input context;
          the backend's decision rules primarily use field water depth
          and forecast data.
        </p>
      </section>

      {irrigationAdvice && (
        <section className="weather-card weather-results">
          <div className="weather-section-heading">
            <div>
              <h2>Irrigation Guidance</h2>
              <p>
                {irrigationAdvice.crop} · {irrigationAdvice.growth_stage}
              </p>
            </div>
            <span className="weather-result-icon">💦</span>
          </div>

          <div className="weather-recommendation">
            <strong>Recommendation</strong>
            <p>{irrigationAdvice.recommendation}</p>
          </div>

          <h3 className="weather-subheading">Three-Day Water Estimates</h3>

          <div className="weather-table-wrapper">
            <table className="weather-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Forecast Rain</th>
                  <th>Rain Chance</th>
                  <th>Reference ET₀</th>
                  <th>Estimated Crop Demand</th>
                  <th>Effective Rain</th>
                </tr>
              </thead>
              <tbody>
                {(irrigationAdvice.three_day_estimates || []).map(
                  (item, index) => (
                    <tr key={item.date || index}>
                      <td>{formatDate(item.date)}</td>
                      <td>{displayValue(item.forecast_rainfall_mm, " mm")}</td>
                      <td>
                        {displayValue(item.rain_probability_percent, "%")}
                      </td>
                      <td>
                        {displayValue(
                          item.reference_evapotranspiration_mm,
                          " mm"
                        )}
                      </td>
                      <td>
                        {displayValue(
                          item.estimated_crop_water_demand_mm,
                          " mm"
                        )}
                      </td>
                      <td>
                        {displayValue(
                          item.estimated_effective_rainfall_mm,
                          " mm"
                        )}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>

          {irrigationAdvice.method?.note && (
            <p className="weather-footnote">
              {irrigationAdvice.method.note}
            </p>
          )}
        </section>
      )}

      <section className="weather-card crop-recommendation-input">
        <div className="weather-section-heading">
          <div>
            <h2>Crop-Specific Recommendations</h2>
            <p>Select a crop supported by your backend rules.</p>
          </div>
          <span className="weather-result-icon">🌿</span>
        </div>

        <div className="weather-crop-form">
          <label className="weather-field">
            <span>Crop</span>
            <select value={crop} onChange={(event) => setCrop(event.target.value)}>
              {cropOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={loadAgricultureRecommendations}
            disabled={Boolean(loading)}
          >
            {loading === "recommendations"
              ? "Generating..."
              : "Generate Crop Advice"}
          </button>
        </div>
      </section>

      {agricultureAdvice && (
        <section className="weather-card weather-results">
          <div className="weather-section-heading">
            <div>
              <h2>Weather Alerts &amp; Crop Advice</h2>
              <p>
                {agricultureAdvice.crop} ·{" "}
                {agricultureAdvice.location?.timezone || "Local timezone"}
              </p>
            </div>
            <span className="weather-result-icon">📋</span>
          </div>

          <div className="weather-metric-grid">
            <div className="weather-metric">
              <span>Temperature</span>
              <strong>
                {displayValue(
                  agricultureAdvice.current_weather?.temperature_celsius,
                  " °C"
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Humidity</span>
              <strong>
                {displayValue(
                  agricultureAdvice.current_weather
                    ?.relative_humidity_percent,
                  "%"
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Wind Speed</span>
              <strong>
                {displayValue(
                  agricultureAdvice.current_weather?.wind_speed_kmh,
                  " km/h"
                )}
              </strong>
            </div>

            <div className="weather-metric">
              <span>Precipitation</span>
              <strong>
                {displayValue(
                  agricultureAdvice.current_weather?.precipitation_mm,
                  " mm"
                )}
              </strong>
            </div>
          </div>

          <h3 className="weather-subheading">Recommendations &amp; Alerts</h3>

          <div className="weather-alert-list">
            {(agricultureAdvice.recommendations || []).map(
              (item, index) => (
                <article
                  className={`weather-alert weather-alert-${item.priority || "low"}`}
                  key={`${item.type || "advice"}-${item.date || index}`}
                >
                  <div className="weather-alert-topline">
                    <strong>{readableLabel(item.type)}</strong>
                    <span>{readableLabel(item.priority || "low")} priority</span>
                  </div>

                  {item.crop && (
                    <p className="weather-alert-crop">
                      Crop: {item.crop}
                    </p>
                  )}

                  {item.date && (
                    <p className="weather-alert-date">
                      Forecast date: {formatDate(item.date)}
                    </p>
                  )}

                  <p>{item.message}</p>
                </article>
              )
            )}
          </div>

          <h3 className="weather-subheading">Three-Day Weather Outlook</h3>

          <div className="weather-table-wrapper">
            <table className="weather-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Maximum Temp.</th>
                  <th>Rainfall</th>
                  <th>Rain Chance</th>
                </tr>
              </thead>
              <tbody>
                {(agricultureAdvice.three_day_forecast || []).map(
                  (item, index) => (
                    <tr key={item.date || index}>
                      <td>{formatDate(item.date)}</td>
                      <td>
                        {displayValue(
                          item.maximum_temperature_celsius,
                          " °C"
                        )}
                      </td>
                      <td>{displayValue(item.rainfall_mm, " mm")}</td>
                      <td>
                        {displayValue(item.rain_probability_percent, "%")}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>

          {agricultureAdvice.note && (
            <p className="weather-footnote">{agricultureAdvice.note}</p>
          )}
        </section>
      )}

      <p className="weather-disclaimer">
        <strong>Important:</strong> Weather-based recommendations use
        preliminary rules and estimated values. Check actual field
        conditions and local agricultural guidance before making
        irrigation decisions.
      </p>
    </div>
  );
}