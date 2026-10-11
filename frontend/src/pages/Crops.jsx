import { useEffect, useState } from "react";
import api from "../services/api";
import "./Crops.css";

export default function Crops() {
  const [crops, setCrops] = useState([]);
  const [name, setName] = useState("");
  const [variety, setVariety] = useState("");
  const [season, setSeason] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadCrops() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/crops");
      const data = response.data;

      setCrops(
        Array.isArray(data)
          ? data
          : Array.isArray(data?.crops)
            ? data.crops
            : []
      );

      if (!Array.isArray(data) && !Array.isArray(data?.crops)) {
        setError("The crops API returned an unexpected response format.");
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not load crops. Please check your login and backend."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCrops();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);

    try {
      await api.post("/crops", {
        name: name.trim(),
        variety: variety.trim(),
        season: season.trim(),
      });

      setName("");
      setVariety("");
      setSeason("");
      setSuccess("Crop added successfully!");
      await loadCrops();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not add the crop. Please check the entered details."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="crops-page">
      <div className="crops-heading">
        <div>
          <p className="crops-eyebrow">SMART AGRICULTURE</p>
          <h1>Crop Management</h1>
          <p>Manage your crops and keep your farming records organized.</p>
        </div>

        <button
          className="crop-refresh"
          type="button"
          onClick={loadCrops}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh crops"}
        </button>
      </div>

      {error && <div className="crop-message crop-error">{String(error)}</div>}
      {success && (
        <div className="crop-message crop-success">{success}</div>
      )}

      <section className="crop-panel">
        <h2>Add a new crop</h2>
        <p className="crop-panel-description">
          Enter the crop details below.
        </p>

        <form className="crop-form" onSubmit={handleSubmit}>
          <div className="crop-field">
            <label htmlFor="crop-name">Crop name</label>
            <input
              id="crop-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="e.g. Rice"
              required
            />
          </div>

          <div className="crop-field">
            <label htmlFor="crop-variety">Variety</label>
            <input
              id="crop-variety"
              value={variety}
              onChange={(event) => setVariety(event.target.value)}
              placeholder="e.g. Basmati"
              required
            />
          </div>

          <div className="crop-field">
            <label htmlFor="crop-season">Season</label>
            <select
              id="crop-season"
              value={season}
              onChange={(event) => setSeason(event.target.value)}
              required
            >
              <option value="">Select season</option>
              <option value="Kharif">Kharif</option>
              <option value="Rabi">Rabi</option>
              <option value="Zaid">Zaid</option>
              <option value="Perennial">Perennial</option>
            </select>
          </div>

          <button className="crop-submit" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Add crop"}
          </button>
        </form>
      </section>

      <section className="crop-panel">
        <div className="crop-list-heading">
          <div>
            <h2>Your crops</h2>
            <p className="crop-panel-description">
              Crops retrieved from your database.
            </p>
          </div>

          <span className="crop-count">{crops.length} crops</span>
        </div>

        {loading ? (
          <p className="crop-empty">Loading crop records...</p>
        ) : crops.length === 0 ? (
          <p className="crop-empty">
            No crops found. Use the form above to add your first crop.
          </p>
        ) : (
          <div className="crop-table-wrapper">
            <table className="crop-table">
              <thead>
                <tr>
                  <th>Crop name</th>
                  <th>Variety</th>
                  <th>Season</th>
                </tr>
              </thead>

              <tbody>
                {crops.map((crop, index) => (
                  <tr key={crop.id ?? index}>
                    <td>{crop.name ?? "—"}</td>
                    <td>{crop.variety ?? "—"}</td>
                    <td>
                      <span className="crop-season">
                        {crop.season ?? "—"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}