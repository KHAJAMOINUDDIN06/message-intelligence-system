# Message Intelligence System

An AI/ML-based message processing system that analyzes messages, classifies their intent, extracts actionable tasks and events, detects sensitive information, and validates mandatory fields.

## 🚀 Overview

The Message Intelligence System processes large collections of messages and converts unstructured text into structured, actionable information.

The system performs:

- Message classification
- Task and event extraction
- Sensitive information detection
- Sensitive value masking
- Mandatory field validation
- Chronological message processing
- Automated testing

The project is designed with a modular Python architecture so that each processing component can be tested and maintained independently.

---

## ✨ Key Features

### 1. Message Classification

Each message is categorized into one of six categories:

- Action Required
- General Information
- Meeting or Event
- Personal Information
- Promotional
- Sensitive Information

### 2. Task and Event Extraction

The system identifies actionable information such as:

- Tasks
- Meetings
- Events
- Dates
- Times
- Deadlines
- Priority information

The system does not invent missing dates or information.

### 3. Sensitive Information Detection

The system detects sensitive information such as:

- OTPs
- PINs
- Passwords

Sensitive values are masked before being included in analysis results.

### 4. Mandatory Field Validation

Extracted information is validated to ensure required fields are present and valid.

### 5. Automated Testing

The project includes automated tests using `pytest`.

Current test result:

**18/18 tests passed successfully.**

---

## 🏗️ System Architecture

```text
Input Messages
      │
      ▼
┌──────────────────────┐
│ Message Preprocessing│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Message Classifier   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Entity / Task        │
│ Event Extraction     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Sensitive Information│
│ Detection & Masking  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Mandatory Field      │
│ Validation           │
└──────────┬───────────┘
           │
           ▼
     Structured Outputs