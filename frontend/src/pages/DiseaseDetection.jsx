
import { useEffect, useState } from "react";
import api from "../services/api";
import "./DiseaseDetection.css";

function DiseaseDetection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedFile) {
      setPreview("");
      return;
    }

    const imageUrl = URL.createObjectURL(selectedFile);
    setPreview(imageUrl);

    return () => URL.revokeObjectURL(imageUrl);
  }, [selectedFile]);

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    setResult(null);
    setError("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!file.type.startsWith("image/")) {
      setSelectedFile(null);
      setError("Please select a valid image file.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setSelectedFile(null);
      setError("Please select an image smaller than 10 MB.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  }

  async function handlePrediction() {
    if (!selectedFile) {
      setError("Please upload a crop leaf image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await api.post(
        "/disease/predict",
        formData
      );

      setResult(response.data);
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : err.response
            ? `Prediction failed (HTTP ${err.response.status}).`
            : "Cannot connect to the backend. Check that FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setSelectedFile(null);
    setResult(null);
    setError("");

    const fileInput = document.getElementById(
      "disease-image-input"
    );

    if (fileInput) {
      fileInput.value = "";
    }
  }

  const confidencePercent =
    result && Number.isFinite(Number(result.confidence))
      ? Math.max(
          0,
          Math.min(100, Number(result.confidence) * 100)
        )
      : null;

  const diseaseName = result?.predicted_disease
    ? result.predicted_disease
        .replaceAll("_", " ")
        .replace(/\s+/g, " ")
        .trim()
    : "";

  return (
    <div className="disease-page">
      <section className="disease-intro">
        <div className="disease-intro-icon">🔬</div>

        <div>
          <p className="disease-eyebrow">
            AI-POWERED PLANT HEALTH
          </p>

          <h2>Plant Disease Detection</h2>

          <p>
            Upload a crop leaf image to let your trained AI model
            identify a possible plant disease.
          </p>
        </div>
      </section>

      <div className="disease-content">
        <section className="disease-card">
          <div className="disease-card-heading">
            <span className="disease-step">01</span>

            <div>
              <h3>Upload leaf image</h3>
              <p>Choose a clear image of the affected leaf.</p>
            </div>
          </div>

          <label
            className={`disease-upload ${
              preview ? "has-image" : ""
            }`}
            htmlFor="disease-image-input"
          >
            {preview ? (
              <img
                className="disease-preview"
                src={preview}
                alt="Selected crop leaf preview"
              />
            ) : (
              <div className="disease-upload-placeholder">
                <span className="disease-upload-icon">📷</span>
                <strong>Choose a leaf image</strong>
                <span>JPG, PNG, or another supported image format</span>
                <span>Maximum file size: 10 MB</span>
              </div>
            )}
          </label>

          <input
            id="disease-image-input"
            className="disease-file-input"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
          />

          {selectedFile && (
            <div className="disease-file-info">
              <span className="disease-file-icon">🖼️</span>

              <div className="disease-file-details">
                <strong>{selectedFile.name}</strong>
                <span>
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>

              <button
                type="button"
                className="disease-remove-button"
                onClick={resetForm}
                disabled={loading}
              >
                Remove
              </button>
            </div>
          )}

          {error && (
            <div className="disease-error" role="alert">
              <strong>Unable to predict</strong>
              <p>{error}</p>
            </div>
          )}

          <button
            type="button"
            className="disease-predict-button"
            onClick={handlePrediction}
            disabled={!selectedFile || loading}
          >
            {loading ? (
              <>
                <span className="disease-spinner" />
                Analyzing image...
              </>
            ) : (
              <>🔍 Detect Disease</>
            )}
          </button>

          <p className="disease-privacy-note">
            Your image is sent to your Smart Agriculture AI backend
            for prediction.
          </p>
        </section>

        <section className="disease-card disease-result-card">
          <div className="disease-card-heading">
            <span className="disease-step">02</span>

            <div>
              <h3>Prediction result</h3>
              <p>Your model's response will appear here.</p>
            </div>
          </div>

          {result ? (
            <div className="disease-result">
              <div className="disease-success-icon">✓</div>

              <span className="disease-result-label">
                PREDICTED CONDITION
              </span>

              <h3>{diseaseName}</h3>

              {confidencePercent !== null && (
                <div className="disease-confidence">
                  <div className="disease-confidence-heading">
                    <span>Model confidence</span>
                    <strong>
                      {confidencePercent.toFixed(2)}%
                    </strong>
                  </div>

                  <div
                    className="disease-confidence-track"
                    role="progressbar"
                    aria-label="Model confidence"
                    aria-valuenow={confidencePercent}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="disease-confidence-fill"
                      style={{
                        width: `${confidencePercent}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              <div className="disease-result-file">
                <span>Analyzed image</span>
                <strong>{result.filename || selectedFile?.name}</strong>
              </div>

              <div className="disease-disclaimer">
                <strong>Important</strong>
                <p>
                  This is an AI-generated prediction, not a confirmed
                  diagnosis. Check the plant carefully and consult an
                  agricultural expert before choosing treatment.
                </p>
              </div>

              <button
                type="button"
                className="disease-secondary-button"
                onClick={resetForm}
              >
                Analyze another image
              </button>
            </div>
          ) : (
            <div className="disease-empty-result">
              <div className="disease-empty-icon">🌿</div>

              <h3>Ready to analyze</h3>

              <p>
                Select a leaf image and click Detect Disease.
                Your prediction and confidence score will appear here.
              </p>

              <div className="disease-result-tip">
                <strong>Tip for better results</strong>
                <p>
                  Use a clear, well-lit image with the leaf visible
                  and in focus.
                </p>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default DiseaseDetection;
