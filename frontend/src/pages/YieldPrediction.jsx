import { useState } from "react";
import api from "../services/api";
import "./YieldPrediction.css";

const crops = [
  "Barley",
  "Castor",
  "Chickpea",
  "Cotton",
  "Finger Millet",
  "Groundnut",
  "Linseed",
  "Maize",
  "Minor Pulses",
  "Pearl Millet",
  "Pigeonpea",
  "Rapeseed & Mustard",
  "Rice",
  "Safflower",
  "Sesamum",
  "Sorghum (Kharif)",
  "Sorghum (Rabi)",
  "Soybean",
  "Sugarcane",
  "Sunflower",
  "Wheat",
];

const seasons = ["Kharif", "Rabi", "Whole Year"];

const soilTypes = [
  "Alfisols",
  "Aridisols",
  "Entisols",
  "Inceptisols",
  "Mollisols",
  "Vertisols",
];

// These are exact region names found in your training dataset.
// You can also type another region using its exact dataset spelling.
const commonRegions = [
  "Coimbatore, Tamil Nadu",
  "Madurai, Tamil Nadu",
  "Salem, Tamil Nadu",
  "Thanjavur, Tamil Nadu",
  "Kanyakumari, Tamil Nadu",
  "Alappuzha, Kerala",
  "Bangalore, Karnataka",
  "Hyderabad, Telangana",
  "Pune, Maharashtra",
  "Ahmedabad, Gujarat",
  "Jaipur, Rajasthan",
  "Ludhiana, Punjab",
  "Amritsar, Punjab",
  "Karnal, Haryana",
  "Lucknow, Uttar Pradesh",
  "Agra, Uttar Pradesh",
  "Patna, Bihar",
  "Cuttack, Odisha",
  "Guntur, AndhraPradesh",
  "Indore, Madhya Pradesh",
];

const initialForm = {
  year: "2026",
  region: "Coimbatore, Tamil Nadu",
  crop: "Rice",
  season: "Kharif",
  temperature: "",
  rainfall: "",
  humidity: "",
  soil_type: "Inceptisols",
  ph: "",
  nitrogen: "",
  phosphorus: "",
  potassium: "",
  fertilizer: "",
  pesticide: "",
};

const numericFields = [
  {
    name: "year",
    label: "Year",
    type: "number",
    min: 1900,
    max: 2100,
    step: 1,
    placeholder: "e.g. 2026",
  },
  {
    name: "temperature",
    label: "Temperature (°C)",
    type: "number",
    min: -20,
    max: 60,
    step: "any",
    placeholder: "e.g. 28",
  },
  {
    name: "rainfall",
    label: "Rainfall",
    type: "number",
    min: 0,
    step: "any",
    placeholder: "Enter rainfall",
  },
  {
    name: "humidity",
    label: "Humidity (%)",
    type: "number",
    min: 0,
    max: 100,
    step: "any",
    placeholder: "e.g. 65",
  },
  {
    name: "ph",
    label: "Soil pH",
    type: "number",
    min: 0,
    max: 14,
    step: "any",
    placeholder: "e.g. 6.5",
  },
  {
    name: "nitrogen",
    label: "Nitrogen",
    type: "number",
    min: 0,
    step: "any",
    placeholder: "Enter nitrogen value",
  },
  {
    name: "phosphorus",
    label: "Phosphorus",
    type: "number",
    min: 0,
    step: "any",
    placeholder: "Enter phosphorus value",
  },
  {
    name: "potassium",
    label: "Potassium",
    type: "number",
    min: 0,
    step: "any",
    placeholder: "Enter potassium value",
  },
  {
    name: "fertilizer",
    label: "Fertilizer",
    type: "number",
    min: 0,
    step: "any",
    placeholder: "Enter fertilizer value",
  },
  {
    name: "pesticide",
    label: "Pesticide",
    type: "number",
    min: 0,
    step: "any",
    placeholder: "Enter pesticide value",
  },
];

function YieldPrediction() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setError("");
    setResult(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setResult(null);

    // Validate all required inputs before sending the request.
    const missingField = Object.entries(form).find(
      ([, value]) => String(value).trim() === ""
    );

    if (missingField) {
      setError("Please complete all fields before predicting.");
      return;
    }

    const numericValues = numericFields.map((field) => ({
      ...field,
      value: Number(form[field.name]),
    }));

    const invalidNumber = numericValues.find(
      (field) => !Number.isFinite(field.value)
    );

    if (invalidNumber) {
      setError(`Please enter a valid value for ${invalidNumber.label}.`);
      return;
    }

    const year = Number(form.year);

    if (!Number.isInteger(year) || year < 1900 || year > 2100) {
      setError("Please enter a valid year between 1900 and 2100.");
      return;
    }

    if (Number(form.humidity) < 0 || Number(form.humidity) > 100) {
      setError("Humidity must be between 0 and 100.");
      return;
    }

    if (Number(form.ph) < 0 || Number(form.ph) > 14) {
      setError("Soil pH must be between 0 and 14.");
      return;
    }

    if (Number(form.temperature) < -20 || Number(form.temperature) > 60) {
      setError("Please enter a temperature between -20°C and 60°C.");
      return;
    }

    const nonNegativeFields = [
      "rainfall",
      "nitrogen",
      "phosphorus",
      "potassium",
      "fertilizer",
      "pesticide",
    ];

    if (
      nonNegativeFields.some((name) => Number(form[name]) < 0)
    ) {
      setError("Rainfall, nutrient, fertilizer, and pesticide values cannot be negative.");
      return;
    }

    const payload = {
      year,
      region: form.region.trim(),
      crop: form.crop,
      season: form.season,
      temperature: Number(form.temperature),
      rainfall: Number(form.rainfall),
      humidity: Number(form.humidity),
      soil_type: form.soil_type,
      ph: Number(form.ph),
      nitrogen: Number(form.nitrogen),
      phosphorus: Number(form.phosphorus),
      potassium: Number(form.potassium),
      fertilizer: Number(form.fertilizer),
      pesticide: Number(form.pesticide),
    };

    try {
      setLoading(true);

      const response = await api.post("/yield/predict", payload);

      if (
        response.data?.success !== true ||
        !Number.isFinite(Number(response.data?.predicted_yield))
      ) {
        throw new Error("The backend did not return a valid prediction.");
      }

      setResult({
        predictedYield: Number(response.data.predicted_yield),
        crop: form.crop,
        region: form.region.trim(),
        year,
      });
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : err.message || "Unable to predict crop yield. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setForm(initialForm);
    setResult(null);
    setError("");
  }

  return (
    <div className="yield-page">
      <section className="yield-intro">
        <div className="yield-intro-icon">🌾</div>

        <div>
          <span className="yield-eyebrow">MACHINE LEARNING TOOL</span>
          <h2>Crop Yield Prediction</h2>
          <p>
            Enter your farm and soil conditions to estimate crop yield
            using your trained XGBoost model.
          </p>
        </div>
      </section>

      <form className="yield-form" onSubmit={handleSubmit}>
        <div className="yield-section-heading">
          <span className="yield-step">01</span>
          <div>
            <h3>Crop and farm details</h3>
            <p>Choose the crop, season, year, and region.</p>
          </div>
        </div>

        <div className="yield-form-grid">
          <label className="yield-field">
            <span>Crop</span>
            <select name="crop" value={form.crop} onChange={handleChange}>
              {crops.map((crop) => (
                <option key={crop} value={crop}>
                  {crop}
                </option>
              ))}
            </select>
          </label>

          <label className="yield-field">
            <span>Growing season</span>
            <select
              name="season"
              value={form.season}
              onChange={handleChange}
            >
              {seasons.map((season) => (
                <option key={season} value={season}>
                  {season}
                </option>
              ))}
            </select>
          </label>

          <label className="yield-field">
            <span>Region / District</span>
            <input
              type="text"
              name="region"
              list="yield-region-options"
              value={form.region}
              onChange={handleChange}
              placeholder="Enter region exactly as in dataset"
              autoComplete="off"
              required
            />
            <datalist id="yield-region-options">
              {commonRegions.map((region) => (
                <option key={region} value={region} />
              ))}
            </datalist>
            <small>Use an exact region name from the training dataset.</small>
          </label>

          <label className="yield-field">
            <span>Year</span>
            <input
              type="number"
              name="year"
              min="1900"
              max="2100"
              step="1"
              value={form.year}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div className="yield-section-heading">
          <span className="yield-step">02</span>
          <div>
            <h3>Weather and soil conditions</h3>
            <p>Enter measurements using the same units as your dataset.</p>
          </div>
        </div>

        <div className="yield-form-grid">
          {numericFields
            .filter((field) =>
              ["temperature", "rainfall", "humidity"].includes(field.name)
            )
            .map((field) => (
              <label className="yield-field" key={field.name}>
                <span>{field.label}</span>
                <input
                  type={field.type}
                  name={field.name}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={form[field.name]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required
                />
              </label>
            ))}

          <label className="yield-field">
            <span>Soil type</span>
            <select
              name="soil_type"
              value={form.soil_type}
              onChange={handleChange}
            >
              {soilTypes.map((soil) => (
                <option key={soil} value={soil}>
                  {soil}
                </option>
              ))}
            </select>
          </label>

          {numericFields
            .filter((field) => field.name === "ph")
            .map((field) => (
              <label className="yield-field" key={field.name}>
                <span>{field.label}</span>
                <input
                  type={field.type}
                  name={field.name}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={form[field.name]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required
                />
              </label>
            ))}
        </div>

        <div className="yield-section-heading">
          <span className="yield-step">03</span>
          <div>
            <h3>Nutrients and farm inputs</h3>
            <p>Enter the numerical values used by your model.</p>
          </div>
        </div>

        <div className="yield-form-grid">
          {numericFields
            .filter((field) =>
              ["nitrogen", "phosphorus", "potassium", "fertilizer", "pesticide"].includes(
                field.name
              )
            )
            .map((field) => (
              <label className="yield-field" key={field.name}>
                <span>{field.label}</span>
                <input
                  type={field.type}
                  name={field.name}
                  min={field.min}
                  step={field.step}
                  value={form[field.name]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required
                />
              </label>
            ))}
        </div>

        <p className="yield-units-note">
          Important: use the same measurement units as the model's training
          dataset. Do not guess fertilizer, pesticide, rainfall, or nutrient
          units if you are unsure.
        </p>

        {error && (
          <div className="yield-error" role="alert">
            <span>⚠️</span>
            <p>{error}</p>
          </div>
        )}

        <div className="yield-actions">
          <button
            type="button"
            className="yield-reset-button"
            onClick={resetForm}
            disabled={loading}
          >
            Reset form
          </button>

          <button
            type="submit"
            className="yield-submit-button"
            disabled={loading}
          >
            {loading ? "Predicting yield..." : "Predict crop yield →"}
          </button>
        </div>
      </form>

      {result && (
        <section className="yield-result" aria-live="polite">
          <div className="yield-result-top">
            <span className="yield-result-icon">🌱</span>
            <div>
              <span className="yield-eyebrow">PREDICTION COMPLETE</span>
              <h3>Estimated crop yield</h3>
            </div>
          </div>

          <p className="yield-result-number">
            {result.predictedYield.toLocaleString(undefined, {
              maximumFractionDigits: 2,
            })}
          </p>

          <p className="yield-result-unit">
            Predicted value in the model's target units
          </p>

          <div className="yield-result-details">
            <div>
              <span>Crop</span>
              <strong>{result.crop}</strong>
            </div>
            <div>
              <span>Region</span>
              <strong>{result.region}</strong>
            </div>
            <div>
              <span>Year</span>
              <strong>{result.year}</strong>
            </div>
          </div>

          <p className="yield-disclaimer">
            This is a machine-learning estimate based on the supplied inputs,
            not a guarantee of actual harvest. Accuracy depends on input
            quality and how well the training data represents your farm.
          </p>
        </section>
      )}
    </div>
  );
}

export default YieldPrediction;