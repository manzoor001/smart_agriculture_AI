
import { useEffect, useState } from "react";
import api from "../services/api";
import "./SoilFertilizer.css";

const initialSoil = {
  crop_name: "",
  nitrogen: "",
  phosphorus: "",
  potassium: "",
  ph: "",
};

const initialFertilizer = {
  temperature: "26",
  humidity: "70",
  moisture: "40",
  soil_type: "Loamy",
  crop_type: "Wheat",
  nitrogen: "50",
  phosphorus: "40",
  potassium: "40",
};

function getErrorMessage(error) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(", ");
  }

  return (
    error.response?.data?.message ||
    error.message ||
    "Something went wrong. Please try again."
  );
}

function getNpkGrade(recommendation) {
  const value =
    recommendation?.recommended_fertilizer ??
    recommendation?.fertilizer ??
    recommendation?.prediction ??
    recommendation?.recommended_fertilizer_name ??
    "";

  // Support a plain grade or a string such as "NPK fertilizer: 10-26-26".
  if (typeof value === "string" || typeof value === "number") {
    const match = String(value).match(
      /(\d+(?:\.\d+)?)\s*[-–:]\s*(\d+(?:\.\d+)?)\s*[-–:]\s*(\d+(?:\.\d+)?)/
    );

    if (match) {
      return {
        name: String(value),
        nitrogen: match[1],
        phosphate: match[2],
        potash: match[3],
      };
    }

    return {
      name: String(value || "Recommendation received"),
      nitrogen: null,
      phosphate: null,
      potash: null,
    };
  }

  return {
    name: "Recommendation received",
    nitrogen: null,
    phosphate: null,
    potash: null,
  };
}

function getRecordCount(recommendation) {
  const records = recommendation?.nearest_records;

  if (Array.isArray(records)) return records.length;
  if (typeof records === "number") return records;
  if (typeof records === "string" && records.trim() !== "") {
    const count = Number(records);
    return Number.isFinite(count) ? count : null;
  }

  return null;
}

export default function SoilFertilizer() {
  const [soil, setSoil] = useState(initialSoil);
  const [soilRecords, setSoilRecords] = useState([]);
  const [fertilizer, setFertilizer] = useState(initialFertilizer);

  const [soilLoading, setSoilLoading] = useState(true);
  const [soilSaving, setSoilSaving] = useState(false);
  const [fertilizerLoading, setFertilizerLoading] = useState(false);

  const [soilError, setSoilError] = useState("");
  const [soilMessage, setSoilMessage] = useState("");
  const [fertilizerError, setFertilizerError] = useState("");
  const [recommendation, setRecommendation] = useState(null);

  async function loadSoilRecords() {
    setSoilLoading(true);
    setSoilError("");

    try {
      const response = await api.get("/soil/");
      const data = response.data;

      if (Array.isArray(data)) {
        setSoilRecords(data);
      } else if (Array.isArray(data?.records)) {
        setSoilRecords(data.records);
      } else if (Array.isArray(data?.items)) {
        setSoilRecords(data.items);
      } else {
        setSoilRecords([]);
      }
    } catch (error) {
      setSoilError(getErrorMessage(error));
    } finally {
      setSoilLoading(false);
    }
  }

  useEffect(() => {
    loadSoilRecords();
  }, []);

  function handleSoilChange(event) {
    const { name, value } = event.target;
    setSoil((previous) => ({ ...previous, [name]: value }));
  }

  function handleFertilizerChange(event) {
    const { name, value } = event.target;
    setFertilizer((previous) => ({ ...previous, [name]: value }));
  }

  async function handleSoilSubmit(event) {
    event.preventDefault();
    setSoilSaving(true);
    setSoilError("");
    setSoilMessage("");

    try {
      const payload = {
        crop_name: soil.crop_name.trim(),
        nitrogen: Number(soil.nitrogen),
        phosphorus: Number(soil.phosphorus),
        potassium: Number(soil.potassium),
        ph: Number(soil.ph),
      };

      await api.post("/soil/", payload);

      setSoilMessage("Soil record saved successfully.");
      setSoil(initialSoil);
      await loadSoilRecords();
    } catch (error) {
      setSoilError(getErrorMessage(error));
    } finally {
      setSoilSaving(false);
    }
  }

  async function handleFertilizerSubmit(event) {
    event.preventDefault();

    setFertilizerLoading(true);
    setFertilizerError("");
    setRecommendation(null);

    try {
      const payload = {
        temperature: Number(fertilizer.temperature),
        humidity: Number(fertilizer.humidity),
        moisture: Number(fertilizer.moisture),
        soil_type: fertilizer.soil_type,
        crop_type: fertilizer.crop_type,
        nitrogen: Number(fertilizer.nitrogen),
        phosphorus: Number(fertilizer.phosphorus),
        potassium: Number(fertilizer.potassium),
      };

      const response = await api.post(
        "/fertilizer/recommend",
        payload
      );

      const data = response.data;

      if (
        data === null ||
        (typeof data !== "object" && typeof data !== "string")
      ) {
        throw new Error("The API returned an unexpected response.");
      }

      setRecommendation(
        typeof data === "string" ? { recommended_fertilizer: data } : data
      );
    } catch (error) {
      setFertilizerError(getErrorMessage(error));
    } finally {
      setFertilizerLoading(false);
    }
  }

  const grade = recommendation ? getNpkGrade(recommendation) : null;
  const similarRecords = recommendation
    ? getRecordCount(recommendation)
    : null;

  return (
    <div className="sf-page">
      <header className="sf-page-header">
        <div>
          <p className="sf-eyebrow">SMART AGRICULTURE AI</p>
          <h1>Soil &amp; Fertilizer Management</h1>
          <p className="sf-description">
            Manage soil nutrient records and get fertilizer recommendations
            from your machine-learning model.
          </p>
        </div>
      </header>

      <section className="sf-panel">
        <div className="sf-section-heading">
          <span className="sf-section-icon">🧪</span>
          <div>
            <h2>Soil Management</h2>
            <p>Save and review your crop soil nutrient records.</p>
          </div>
        </div>

        <form className="sf-form" onSubmit={handleSoilSubmit}>
          <div className="sf-field">
            <label htmlFor="soil-crop">Crop name</label>
            <input
              id="soil-crop"
              name="crop_name"
              value={soil.crop_name}
              onChange={handleSoilChange}
              placeholder="e.g. Wheat"
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="soil-n">Nitrogen (N)</label>
            <input
              id="soil-n"
              name="nitrogen"
              type="number"
              min="0"
              step="any"
              value={soil.nitrogen}
              onChange={handleSoilChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="soil-p">Phosphorus (P)</label>
            <input
              id="soil-p"
              name="phosphorus"
              type="number"
              min="0"
              step="any"
              value={soil.phosphorus}
              onChange={handleSoilChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="soil-k">Potassium (K)</label>
            <input
              id="soil-k"
              name="potassium"
              type="number"
              min="0"
              step="any"
              value={soil.potassium}
              onChange={handleSoilChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="soil-ph">Soil pH</label>
            <input
              id="soil-ph"
              name="ph"
              type="number"
              min="0"
              max="14"
              step="any"
              value={soil.ph}
              onChange={handleSoilChange}
              required
            />
          </div>

          <div className="sf-form-action">
            <button
              className="sf-button sf-button-primary"
              type="submit"
              disabled={soilSaving}
            >
              {soilSaving ? "Saving..." : "Save soil record"}
            </button>
          </div>
        </form>

        {soilMessage && (
          <p className="sf-alert sf-alert-success" role="status">
            {soilMessage}
          </p>
        )}

        {soilError && (
          <p className="sf-alert sf-alert-error" role="alert">
            {soilError}
          </p>
        )}

        <div className="sf-table-heading">
          <h3>Saved Soil Records</h3>
          <button
            type="button"
            className="sf-button sf-button-secondary"
            onClick={loadSoilRecords}
            disabled={soilLoading}
          >
            {soilLoading ? "Loading..." : "Refresh"}
          </button>
        </div>

        <div className="sf-table-wrap">
          <table className="sf-table">
            <thead>
              <tr>
                <th>Crop</th>
                <th>Nitrogen</th>
                <th>Phosphorus</th>
                <th>Potassium</th>
                <th>pH</th>
              </tr>
            </thead>
            <tbody>
              {soilLoading ? (
                <tr>
                  <td colSpan="5" className="sf-empty">
                    Loading soil records...
                  </td>
                </tr>
              ) : soilRecords.length === 0 ? (
                <tr>
                  <td colSpan="5" className="sf-empty">
                    No soil records found. Add your first record above.
                  </td>
                </tr>
              ) : (
                soilRecords.map((record, index) => (
                  <tr key={record.id ?? index}>
                    <td>{record.crop_name ?? record.crop ?? "—"}</td>
                    <td>{record.nitrogen ?? "—"}</td>
                    <td>{record.phosphorus ?? "—"}</td>
                    <td>{record.potassium ?? "—"}</td>
                    <td>{record.ph ?? record.ph_value ?? "—"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="sf-panel">
        <div className="sf-section-heading">
          <span className="sf-section-icon">🌱</span>
          <div>
            <h2>Fertilizer Recommendation</h2>
            <p>
              Enter crop, soil, nutrient values, and current conditions to
              request a recommendation from your ML model.
            </p>
          </div>
        </div>

        <form className="sf-form" onSubmit={handleFertilizerSubmit}>
          <div className="sf-field">
            <label htmlFor="fert-crop">Crop type</label>
            <select
              id="fert-crop"
              name="crop_type"
              value={fertilizer.crop_type}
              onChange={handleFertilizerChange}
              required
            >
              {[
                "Wheat",
                "Maize",
                "Sugarcane",
                "Cotton",
                "Tobacco",
                "Paddy",
                "Barley",
                "Millets",
                "Pulses",
                "Oil seeds",
                "Ground Nuts",
              ].map((crop) => (
                <option key={crop} value={crop}>
                  {crop}
                </option>
              ))}
            </select>
          </div>

          <div className="sf-field">
            <label htmlFor="fert-soil">Soil type</label>
            <select
              id="fert-soil"
              name="soil_type"
              value={fertilizer.soil_type}
              onChange={handleFertilizerChange}
              required
            >
              {["Loamy", "Sandy", "Black", "Red", "Clayey"].map((soilType) => (
                <option key={soilType} value={soilType}>
                  {soilType}
                </option>
              ))}
            </select>
          </div>

          <div className="sf-field">
            <label htmlFor="fert-temperature">Temperature (°C)</label>
            <input
              id="fert-temperature"
              name="temperature"
              type="number"
              step="any"
              value={fertilizer.temperature}
              onChange={handleFertilizerChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="fert-humidity">Humidity (%)</label>
            <input
              id="fert-humidity"
              name="humidity"
              type="number"
              min="0"
              max="100"
              step="any"
              value={fertilizer.humidity}
              onChange={handleFertilizerChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="fert-moisture">Soil moisture (%)</label>
            <input
              id="fert-moisture"
              name="moisture"
              type="number"
              min="0"
              max="100"
              step="any"
              value={fertilizer.moisture}
              onChange={handleFertilizerChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="fert-n">Nitrogen (N)</label>
            <input
              id="fert-n"
              name="nitrogen"
              type="number"
              min="0"
              step="any"
              value={fertilizer.nitrogen}
              onChange={handleFertilizerChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="fert-p">Phosphorus (P)</label>
            <input
              id="fert-p"
              name="phosphorus"
              type="number"
              min="0"
              step="any"
              value={fertilizer.phosphorus}
              onChange={handleFertilizerChange}
              required
            />
          </div>

          <div className="sf-field">
            <label htmlFor="fert-k">Potassium (K)</label>
            <input
              id="fert-k"
              name="potassium"
              type="number"
              min="0"
              step="any"
              value={fertilizer.potassium}
              onChange={handleFertilizerChange}
              required
            />
          </div>

          <div className="sf-form-action">
            <button
              className="sf-button sf-button-primary"
              type="submit"
              disabled={fertilizerLoading}
            >
              {fertilizerLoading
                ? "Getting recommendation..."
                : "Recommend fertilizer"}
            </button>
          </div>
        </form>

        {fertilizerError && (
          <p className="sf-alert sf-alert-error" role="alert">
            {fertilizerError}
          </p>
        )}

        {recommendation && grade && (
          <div className="fertilizer-result" aria-live="polite">
            <div className="fertilizer-result-heading">
              <span className="fertilizer-icon">🌱</span>
              <div>
                <p className="sf-eyebrow">YOUR ML MODEL RESULT</p>
                <h2>Recommended Fertilizer</h2>
              </div>
            </div>

            <h3 className="fertilizer-grade">{grade.name}</h3>
            <p className="fertilizer-subtitle">
              NPK compound fertilizer grade
            </p>

            {grade.nitrogen !== null &&
            grade.phosphate !== null &&
            grade.potash !== null ? (
              <>
                <h4 className="fertilizer-explanation-title">
                  What do the numbers mean?
                </h4>

                <div className="npk-cards">
                  <div className="npk-card nitrogen">
                    <span className="npk-symbol">N</span>
                    <h3>{grade.nitrogen}%</h3>
                    <p>Nitrogen (N)</p>
                  </div>

                  <div className="npk-card phosphate">
                    <span className="npk-symbol">P</span>
                    <h3>{grade.phosphate}%</h3>
                    <p>Phosphate (P₂O₅)</p>
                  </div>

                  <div className="npk-card potash">
                    <span className="npk-symbol">K</span>
                    <h3>{grade.potash}%</h3>
                    <p>Potash (K₂O)</p>
                  </div>
                </div>
              </>
            ) : (
              <p className="sf-alert sf-alert-info">
                The API returned a recommendation, but its name is not in a
                recognizable three-number NPK format. The percentages are
                hidden to avoid displaying incorrect values.
              </p>
            )}

            {similarRecords !== null && (
              <p className="similar-records">
                Similar dataset records: <strong>{similarRecords}</strong>
              </p>
            )}

            <p className="fertilizer-note">
              Confirm soil test results and local agricultural guidance before
              applying fertilizer to a real field.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
