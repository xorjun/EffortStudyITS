# SCRIPT - Intelligent Tutoring System Documentation

Welcome to the comprehensive documentation for **SCRIPT** (Step-based Coding for Research and Interactive Programming Training), an Intelligent Tutoring System for programming education.

## Overview

SCRIPT is a research-oriented Intelligent Tutoring System developed and maintained by the Knowledge Representation and Machine Learning (KML) group at Bielefeld University. The system provides adaptive programming education through personalized feedback, task selection, and knowledge tracing.

### Key Features

- **Interactive Code Editor**: Monaco-based online code editor with syntax highlighting
- **Adaptive Task Selection**: Personalized task recommendations based on learner competency
- **Multiple Feedback Mechanisms**: 
  - LLM-based feedback (Ollama/OpenAI integration)
  - State-space feedback
  - Unit test-based evaluation
- **Knowledge Tracing**: PFA (Performance Factor Analysis) for modeling learner knowledge
- **Course Management**: Support for multiple courses per user with flexible configuration
- **Code Execution**: Judge0 integration for secure code execution and testing
- **User Management**: Email-based authentication with data collection consent
- **Research Platform**: Designed for educational research with comprehensive data collection

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB with Beanie ODM
- **Authentication**: FastAPI-Users with JWT
- **Code Execution**: Judge0
- **LLM Integration**: Ollama/OpenAI

#### Frontend
- **Framework**: Angular
- **Code Editor**: Monaco Editor
- **UI Components**: Angular Material

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Scheduler**: APScheduler for background tasks

## Project Structure

```
script/
├── api/                      # Backend FastAPI application
│   ├── attempts/            # Code attempt tracking and state logging
│   ├── courses/             # Course management and parsing
│   ├── db/                  # Database connectors (Beanie & Motor)
│   ├── feedback/            # Feedback generation and handling
│   ├── models/              # Pedagogical, domain, and KT models
│   ├── runs/                # Code execution runs
│   ├── services/            # External services (LLM, email, embeddings)
│   ├── submissions/         # Submission handling and evaluation
│   ├── surveys/             # Survey management
│   ├── system/              # System settings and info
│   ├── tasks/               # Task management
│   ├── tests/               # Unit tests
│   └── users/               # User authentication and management
├── courses/                  # Course content and definitions
├── database_scripts/         # MongoDB management scripts
├── frontend/                 # Angular application
│   └── its_ui/              # Angular UI components
├── judge0/                   # Judge0 configuration
├── llm-server/              # LLM server setup (Ollama)
└── doc/                     # Documentation
```

## Documentation Index

### Getting Started
- [Deployment Guide](deployment.md) - Production and Docker deployment
- [Development Setup](development.md) - Local development environment
- [Configuration Reference](configuration.md) - Environment variables and settings

### Architecture
- [System Architecture](architecture.md) - Overall system design
- [API Documentation](api-reference.md) - Complete API endpoints reference
- [Database Schema](database-schema.md) - MongoDB collections and relationships
- [Frontend Architecture](frontend.md) - Angular application structure

### Features & Implementation
- [Models Documentation](models.md) - Pedagogical and knowledge tracing models
- [Course Structure](course-structure.md) - How to create and manage courses
- [Feedback Systems](feedback-systems.md) - LLM and state-space feedback
- [User Journey](user-journey.md) - Learner experience flow

## Quick Start

### For Learners
1. Register with email verification
2. Set data collection preferences
3. Select a course
4. Start solving tasks with interactive feedback
5. Track your progress

### For Educators/Researchers
1. Deploy SCRIPT using Docker
2. Create course content (JSON + Markdown)
3. Configure pedagogical models
4. Enroll learners
5. Collect and analyze learning data

### For Developers
1. Clone the repository
2. Set up local environment (see [Development Setup](development.md))
3. Review [Architecture Documentation](architecture.md)
4. Check [API Reference](api-reference.md)
5. Start contributing

## License

"SCRIPT" is an Intelligent Tutoring System for Programming.

Copyright (C) 2025 Benjamin Paaßen, Jesper Dannath, Alina Deriyeva

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](../LICENSE) for full details.

## Contributing

SCRIPT is actively developed for educational research. Contributions are welcome! Please review the development setup and architecture documentation before contributing.

## Contact

Developed by the Knowledge Representation and Machine Learning (KML) group at Bielefeld University.

Website: https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/kml/

## Research

If you use SCRIPT in your research, please cite our work appropriately. This system is designed to support educational research in programming education, adaptive learning, and intelligent tutoring systems.
