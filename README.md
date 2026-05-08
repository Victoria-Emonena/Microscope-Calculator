# 🔬 Microscope Specimen Size Calculator

**CSC 442 — Computational Biology & Interdisciplinary Studies | Project 1**

A production-ready Streamlit web application that calculates the real-life size of a microscope specimen from its observed (measured) size.

---

## 📌 Features

- **Username login** — required before any calculation
- **Specimen image upload** — JPG/PNG, with preview
- **Microscope type dropdown** — auto-selects magnification factor
  - Light Microscope → 40×
  - Electron Microscope → 1000×
  - Stereo Microscope → 20×
  - Digital Microscope → 200×
- **Unit selection** — nm, µm, mm, cm, m (input & output independently)
- **Formula breakdown** — step-by-step explanation of every calculation
- **SQLite database** — stores username, image, microscope type, sizes, units, timestamp
- **Record management** — view, search, delete individual or all records
- **CSV export** — download all records

---
