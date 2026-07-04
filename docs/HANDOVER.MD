# FloodRisk AI — Project Handover

**Version:** v1.1.0  
**Last Updated:** 2 July 2026  
**Project Status:** MVP Production Ready (Audit Phase)

---

# 1. Project Overview

FloodRisk AI adalah sistem Decision Support berbasis Artificial Intelligence untuk memprediksi Flood Risk Index (FRI) pada komoditas hortikultura menggunakan data cuaca realtime.

Sistem menggabungkan:

- Machine Learning (Random Forest + LSTM)
- Open-Meteo Realtime Weather
- FastAPI Backend
- Next.js Dashboard
- Interactive GIS Map
- AI Decision Support (LLM)

Output utama adalah:

- Flood Risk Index (0–100)
- Risk Level
- Recommendation
- Mitigation

---

# 2. Architecture

## Frontend

Technology

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- Framer Motion
- TanStack Query
- MapLibre GL

Architecture

SPA (Single Page Application)

Layout:

Sidebar
↓

Resizable Panel
↓

Map Container

State menggunakan:

- React Hooks
- TanStack Query
- LocalStorage

Tidak menggunakan Redux atau Zustand.

---

## Database

Technology

Supabase

- PostgreSQL
- Authentication
- Row Level Security (RLS)

---
## Backend

Technology

- FastAPI
- Python 3.12

Semua endpoint berada di:

/api/*

Prediction hanya boleh melalui:

backend/services/prediction_gateway.py

JANGAN memanggil predictor secara langsung.

---

## Machine Learning

Primary Model

Random Forest

Secondary Model

LSTM

Training Dataset

BMKG

726 records

9 Features

Output

Flood Risk Index (0–100)

---

## AI Decision Support

Supported Providers

- OpenAI
- Anthropic
- Gemini
- Groq

LLM hanya digunakan untuk rekomendasi.

LLM tidak digunakan untuk menghasilkan nilai Flood Risk.

---

# 3. Feature List

Model menggunakan tepat 9 feature.

Urutan tidak boleh berubah.

1. rr
2. rain3
3. rain7
4. rain14
5. rh_avg
6. temp_range
7. rainfall_anomaly
8. month
9. day_of_year

Source:

ml/artifacts/feature_list.json

---

# 4. Coding Rules

Selalu baca source code sebelum coding.

Jangan membuat asumsi.

Semua kesimpulan harus berdasarkan source code atau runtime.

Tidak boleh menggunakan:

- any
- unknown as Type

Gunakan:

CSS Variables

Jangan hardcode warna.

Gunakan:

cn()

untuk conditional class.

Semua warna menggunakan design tokens.

---

# 5. Design Rules

Theme

Dark Mode

Map

MapLibre GL

Animation

Framer Motion

Radius

CSS Variables

Risk Color

Low

Green

Medium

Amber

High

Red

---

# 6. Completed Sprints

Backend

✅ ETL

✅ Feature Engineering

✅ FRI Engine

✅ Random Forest

✅ LSTM

✅ DSS Engine

✅ FastAPI

Frontend

✅ UI Foundation

✅ Dashboard

✅ Map

✅ AI Chat

✅ PDF Report

✅ Settings

Documentation

✅ Architecture

✅ Roadmap

✅ Decisions

✅ Research

---

# 7. Current Sprint

MODEL-AUDIT-1.6

Objective

Melakukan validasi scientific terhadap pipeline realtime prediction.

Audit harus membuktikan:

- Feature Engineering benar
- Feature Order benar
- Model Input benar
- Prediction benar
- API Response benar
- Tidak ada feature yang hilang
- Tidak ada pipeline bug

Jika ditemukan bug:

Cari root cause.

Jangan langsung memperbaiki.

---

# 8. Audit Status

MODEL-AUDIT-1

Selesai

MODEL-AUDIT-1.5

Selesai

MODEL-AUDIT-1.6

Sedang berjalan

Target:

Runtime Validation

Pipeline Validation

Root Cause Analysis

Scientific Report

---

# 9. Current Findings

Random Forest berjalan normal.

Inference Pipeline masih perlu divalidasi.

Audit sebelumnya menunjukkan indikasi:

Realtime distribution tidak memiliki nilai pada beberapa engineered feature.

Belum dapat disimpulkan sebagai bug.

Harus dibuktikan melalui runtime validation.

Tidak boleh mengambil kesimpulan tanpa evidence.

---

# 10. Known Technical Debt

DEC-006

Theme default mismatch.

DEC-008

Sidebar collapse belum digunakan.

DEC-010

LLM API Key masih client-side.

DEC-011

print.css masih manual copy.

---

# 11. Future Roadmap

Setelah audit selesai:

1.

Authentication

2.

User Registration

3.

Login Interface

4.

Backend Authentication

5.

Session Management

6.

Analytics V2

7.

Historical Prediction

8.

7-Day Forecast

9.

Notification System

10.

Multi Language

---

# 12. Authentication Design (Planned)

Authentication hanya digunakan untuk:

- Login
- Register
- Session

Database TIDAK menyimpan:

- hasil prediksi
- histori prediksi
- data cuaca

Semua prediksi bersifat realtime.

User hanya melakukan monitoring.

Besok dapat melakukan prediksi kembali pada wilayah berbeda.

---

# 13. Instructions for AI Coding Agents

Before writing code:

1. Read this document.
2. Read the relevant source code.
3. Explain your understanding.
4. Wait for instructions.

Never:

- Guess
- Assume
- Retrain models
- Modify ML artifacts
- Modify backend without approval

Always:

- Read source code first.
- Support conclusions with evidence.
- Explain root cause before proposing fixes.


## ML Audit Status

Date:
2 July 2026

Status:
Completed

Summary:
- Inference pipeline validated.
- Feature engineering validated.
- Random Forest validated.
- No evidence supporting retraining.
- ML subsystem frozen until new evidence (performance degradation, concept drift, or significant new BMKG data) justifies retraining.


# Roadmap After ML Audit

## AUTH-1 — Database Foundation (Supabase)

Objective

Establish the production database infrastructure.

Scope

- Create Supabase project
- Configure PostgreSQL database
- Configure Row Level Security (RLS)
- Configure Authentication
- Environment configuration
- Database migration system
- Initial database schema

Deliverables

- Supabase project
- Database connection
- Initial migration
- Database documentation

---

## AUTH-2 — Authentication Backend

Objective

Implement secure authentication.

Scope

- User registration API
- User login API
- JWT session
- Password hashing
- Protected API middleware
- User profile endpoint

Database

users

---

## AUTH-3 — Authentication Frontend

Objective

Create authentication interface.

Scope

- Login page
- Register page
- Forgot password
- Session persistence
- Route protection
- Logout

---

## AUTH-4 — User Preferences

Scope

- Theme preference
- Default region
- Default prediction model
- Profile settings

---

## AUTH-5 — AI Conversation Persistence

Scope

- Conversation history
- Region-based conversation
- Chat persistence
- Conversation management

---

Future Sprints

- Analytics V2
- Historical Prediction
- 7-Day Forecast
- Notification System
- Multi-language
- Mobile Responsive