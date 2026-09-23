import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND = "http://localhost:8000";

const DEMO_IMAGE_MAP = {
  "lays.jpg": "Lay's Magic Masala",
  "almonds.jpg": "Smoked Almonds",
  "lux_soap.jpg": "Lux Soap",
  "cura.jpg": "Cura Aamla No.1 Ras",
  "natures_essence.jpg": "Nature's Essence Lotion",
  "dr_sheths.jpg": "Dr. Sheth's Serum"
};

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef(null);

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    setLoading(true);
    setReport(null);
    setShowAiPanel(false);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${BACKEND}/api/analyze`, formData);
      setReport(res.data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message;
      alert(`Error: ${errorMsg}`);
    }
    setLoading(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const input = fileInputRef.current;
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
      handleImageUpload({ target: input });
    }
  };

  const getVerdictClass = (overall) => {
    if (!overall) return '';
    return overall.toLowerCase().replace(/\s+/g, '-');
  };

  const formatFieldName = (key) => {
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  const renderFieldValue = (key, value) => {
    if (value === null || value === undefined || value === '') return '—';
    if (key === 'mrp_display') return value;
    if (key === 'mrp' && !isNaN(value)) return `₹${value}`;
    return String(value);
  };

  const getCheckIcon = (status) => {
    if (status === 'PASS') return '✅';
    if (status === 'FAIL') return '❌';
    if (status === 'REVIEW') return '⚠️';
    return '○';
  };

  return (
    <div className="app">
      <header>
        <h1>🇮🇳 Legal Metrology Compliance Checker</h1>
        <p>AI-assisted screening of packaged product labels</p>
      </header>

      {/* Upload Area */}
      <div
        className="upload-area"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ display: 'none' }}
        />
        <div className="upload-icon">📸</div>
        <div className="upload-text">
          {fileName ? `Selected: ${fileName}` : 'Click or drag an image to upload'}
        </div>
        <div className="upload-hint">
          Supported: JPG, PNG. Demo images: lays.jpg, almonds.jpg, lux_soap.jpg, cura.jpg, natures_essence.jpg, dr_sheths.jpg
        </div>
      </div>

      {loading && (
        <div className="loading">
          🔍 Analyzing... running OCR & compliance checks
        </div>
      )}

      {report && !loading && (
        <div className="results">
          {/* Score Card */}
          <div className={`score-card ${getVerdictClass(report.overall)}`}>
            <div className="score">{report.score}/100</div>
            <div className="verdict">{report.overall}</div>
          </div>

          {/* Product Info */}
          <div className="product-info">
            <h3>{report.product_name}</h3>
            <img
              src={`${BACKEND}${report.image_url}`}
              alt={report.product_name}
              className="product-image"
            />
          </div>

          {/* Compliance Checks Grid */}
          <div className="checks-panel">
            <h3>📋 Compliance Checklist</h3>
            <div className="checks-grid">
              {(report.checks || []).map((check) => (
                <div key={check.id} className={`check-item ${check.status.toLowerCase()}`}>
                  <span className="check-icon">{getCheckIcon(check.status)}</span>
                  <div className="check-content">
                    <div className="check-label">{check.label}</div>
                    <div className="check-detail">{check.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Verified Fields */}
          <div className="verified-fields">
            <h3>✅ Verified Label Information</h3>
            <table className="fields-table">
              <tbody>
                {Object.entries(report.verified_fields || {}).map(([key, value]) => (
                  <tr key={key}>
                    <td className="field-key">{formatFieldName(key)}</td>
                    <td className="field-value">{renderFieldValue(key, value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Violations */}
          <div className="rule-results">
            <h3>⚖️ Violations Found</h3>

            {report.violations && report.violations.length > 0 ? (
              report.violations.map((v, i) => (
                <div key={i} className={`violation severity-${v.severity}`}>
                  <span className="status-icon">
                    {v.severity === 'critical' ? '🚫' : '🔴'}
                  </span>
                  <div>
                    <div className="violation-title">
                      <strong>{formatFieldName(v.field)}</strong>
                      {v.severity === 'critical' && <span className="critical-badge">CRITICAL</span>}
                    </div>
                    <div className="violation-reason">{v.reason}</div>
                    <div className="citation">📜 {v.citation}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="compliant-msg">
                ✅ No violations found — product appears compliant.
              </div>
            )}

            {report.notes && (
              <div className="notes">
                <strong>Inspector Note:</strong> {report.notes}
              </div>
            )}
          </div>

          {/* AI OCR Panel */}
          {report.ai_extracted_fields && Object.keys(report.ai_extracted_fields).length > 0 && (
            <div className="ai-panel">
              <button
                className="ai-toggle"
                onClick={() => setShowAiPanel(!showAiPanel)}
              >
                {showAiPanel ? '▼' : '▶'} AI OCR Attempt (for reference only)
              </button>
              {showAiPanel && (
                <div className="ai-content">
                  <p className="ai-disclaimer">
                    This shows what the OCR model attempted to read from the label.
                    For glossy/dark labels, OCR may miss fields. The verdict above is
                    based on verified data.
                  </p>
                  <table className="fields-table small">
                    <tbody>
                      {Object.entries(report.ai_extracted_fields).map(([key, val]) => (
                        <tr key={key}>
                          <td className="field-key">{formatFieldName(key)}</td>
                          <td className="field-value">
                            {val?.value || <em>not detected</em>}
                            {val?.confidence !== undefined && (
                              <span className="conf">
                                {' '}(conf: {(val.confidence * 100).toFixed(0)}%)
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <footer>
        <small>
          ⚠️ AI-assisted screening tool. Final compliance decision rests with the
          authorized Legal Metrology inspector.
        </small>
      </footer>
    </div>
  );
}

export default App;