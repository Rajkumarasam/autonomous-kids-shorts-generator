# Autonomous Kids Shorts Generator

A powerful, AI-driven platform for automatically generating engaging short-form video content tailored for children. This project leverages cutting-edge technologies to create educational, entertaining, and age-appropriate content without manual production overhead.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Support](#support)

## 🎯 Overview

The Autonomous Kids Shorts Generator is a sophisticated system designed to:

- **Automatically generate** short-form video content (15-60 seconds) optimized for children
- **Ensure safety** through content filtering and age-appropriate guardrails
- **Customize themes** based on educational topics, entertainment genres, or learning objectives
- **Scale production** from dozens to thousands of videos with minimal human intervention
- **Maintain quality** through AI-powered review and optimization systems

This project combines natural language processing, computer vision, audio synthesis, and video composition to deliver production-ready short-form content.

## ✨ Features

### Core Capabilities

- **Intelligent Content Generation**
  - AI-powered script generation based on topics and learning objectives
  - Automatic scene and storyboard creation
  - Context-aware dialogue and narration
  - Multi-language support

- **Audio & Voice**
  - Text-to-speech synthesis with child-friendly voices
  - Automatic background music selection and mixing
  - Sound effect placement and timing
  - Audio normalization and quality enhancement

- **Visual Content**
  - Automated scene generation and composition
  - Character animation and motion synthesis
  - Dynamic transitions and effects
  - Brand and theme customization

- **Quality Assurance**
  - Content safety filtering
  - Age-appropriateness verification
  - Educational value assessment
  - Automated quality scoring

- **Management & Analytics**
  - Video library organization
  - Performance analytics and engagement metrics
  - Batch processing capabilities
  - Version control and iteration history

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 16+** (for frontend components)
- **FFmpeg 4.4+** (for video processing)
- **Docker & Docker Compose** (recommended for containerized deployment)
- **Git** (for version control)
- **API Keys**: OpenAI, ElevenLabs, or comparable AI services

### System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 50GB+ for video processing cache
- **GPU**: CUDA 11.0+ compatible GPU (optional but recommended for faster processing)

### Quick Start (5 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rajkumarasam/autonomous-kids-shorts-generator.git
   cd autonomous-kids-shorts-generator
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Run the application**
   ```bash
   python main.py
   # or with Docker
   docker-compose up
   ```

5. **Access the web interface**
   - Open http://localhost:3000 in your browser

## 📦 Installation

### Standard Installation

```bash
# Clone repository
git clone https://github.com/Rajkumarasam/autonomous-kids-shorts-generator.git
cd autonomous-kids-shorts-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Build frontend
npm run build
```

### Docker Installation

```bash
# Build Docker image
docker build -t kids-shorts-generator .

# Run container
docker run -p 3000:3000 -v $(pwd)/videos:/app/videos kids-shorts-generator

# Or use Docker Compose
docker-compose up -d
```

### Development Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt
npm install --save-dev

# Set up pre-commit hooks
pre-commit install

# Run with hot-reload
npm run dev
python -m flask --app main --debug
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
OPENAI_API_KEY=sk-your-key-here
ELEVEN_LABS_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here

# Application Settings
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO
MAX_WORKERS=4

# Video Generation
VIDEO_DURATION_MIN=15
VIDEO_DURATION_MAX=60
TARGET_RESOLUTION=1080p
FRAME_RATE=30
BITRATE=5000k

# Content Safety
ENABLE_CONTENT_FILTERING=True
MIN_AGE_RATING=4
MAX_AGE_RATING=12
BLOCK_EXPLICIT_CONTENT=True

# Storage & Processing
OUTPUT_DIR=./videos
TEMP_DIR=./temp
MAX_CONCURRENT_JOBS=3
VIDEO_CACHE_SIZE=50GB

# Database
DATABASE_URL=sqlite:///kids_shorts.db
# or PostgreSQL: postgresql://user:password@localhost/kids_shorts

# Logging
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=10
```

### Configuration File

Create `config.yaml` for advanced settings:

```yaml
generation:
  script_engine: openai
  animation_engine: stable-diffusion
  voice_provider: elevenlabs
  max_retries: 3

content_safety:
  enable_filtering: true
  profanity_filter: true
  violence_threshold: 0.1
  inappropriate_threshold: 0.2

video:
  resolution: 1080p
  aspect_ratio: "9:16"
  frame_rate: 30
  codec: h264

output:
  format: mp4
  compression_level: medium
  watermark: true
```

## 💻 Usage

### Web Interface

1. **Create a Project**
   - Click "New Project"
   - Enter project name and description
   - Select target age group and educational focus

2. **Generate Videos**
   - Provide topic or learning objective
   - Configure generation parameters
   - Click "Generate" and monitor progress

3. **Review and Edit**
   - Preview generated videos
   - Edit scripts, scenes, or audio
   - Apply custom branding or themes

4. **Export and Share**
   - Download videos in multiple formats
   - Share directly to platforms (YouTube, TikTok)
   - Archive in library for future reference

### Command Line Interface

```bash
# Generate a single video
python cli.py generate --topic "Learning Shapes" --duration 30

# Batch generation
python cli.py batch-generate --config batch_config.json

# Process existing content
python cli.py process --input-dir ./raw_content --output-dir ./processed

# Quality check
python cli.py validate --video videos/output.mp4

# Generate report
python cli.py report --date-range "2026-01-01:2026-01-31" --format html
```

### Python API

```python
from kids_shorts_generator import VideoGenerator, ContentManager

# Initialize generator
generator = VideoGenerator(api_key="your-key")

# Define generation parameters
params = {
    "topic": "The Water Cycle",
    "duration": 45,
    "age_group": "6-8",
    "style": "animated",
    "language": "en"
}

# Generate video
video = generator.generate(params)

# Access video details
print(f"Video ID: {video.id}")
print(f"Duration: {video.duration}s")
print(f"Status: {video.status}")

# Save video
video.save("output/water_cycle.mp4")
```

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                 User Interface Layer                 │
│          (Web Dashboard / Mobile App)                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│            API & Orchestration Layer                │
│   (REST API / WebSocket / Message Queue)            │
└────────────────┬─────────────────┬──────────────────┘
                 │                 │
    ┌────────────▼──┐   ┌──────────▼──────────┐
    │ Script Engine │   │ Media Processing    │
    │ (NLP/LLM)     │   │ Pipeline            │
    └────────────┬──┘   └────────┬────────────┘
                 │                 │
    ┌────────────▼──────────────────▼──────────┐
    │   Content Safety & QA Layer               │
    │ (Filtering / Validation / Scoring)        │
    └────────────┬──────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────┐
    │      Storage & Distribution Layer         │
    │  (Video Library / CDN / Export)           │
    └──────────────────────────────────────────┘
```

### Components

- **Frontend**: React/Vue.js dashboard with real-time updates
- **Backend**: Python Flask/FastAPI with async task processing
- **Video Engine**: FFmpeg with custom processing pipelines
- **AI Services**: OpenAI (GPT-4), ElevenLabs, Stable Diffusion
- **Database**: PostgreSQL for metadata, SQLite for development
- **Cache**: Redis for job queuing and caching
- **Storage**: Local filesystem, S3-compatible, or Cloud Storage

## 📚 API Reference

### Generate Video Endpoint

```
POST /api/v1/videos/generate
Content-Type: application/json

{
  "topic": "string (required)",
  "duration": "integer (15-60, default: 30)",
  "age_group": "string (3-5, 6-8, 9-12)",
  "style": "string (animated, live-action, mixed)",
  "language": "string (en, es, fr, etc.)",
  "educational_focus": "string",
  "custom_characters": "boolean",
  "music_style": "string"
}

Response (200):
{
  "video_id": "uuid",
  "status": "processing",
  "estimated_completion": "2026-01-03T16:15:00Z",
  "progress": 0,
  "created_at": "2026-01-03T16:00:00Z"
}
```

### Get Video Status

```
GET /api/v1/videos/{video_id}

Response (200):
{
  "video_id": "uuid",
  "status": "completed",
  "progress": 100,
  "duration": 30,
  "file_size": 45000000,
  "download_url": "https://...",
  "thumbnail_url": "https://...",
  "quality_score": 0.92,
  "created_at": "2026-01-03T16:00:00Z",
  "completed_at": "2026-01-03T16:12:45Z"
}
```

### List Videos

```
GET /api/v1/videos?limit=20&offset=0&sort=-created_at

Response (200):
{
  "total": 150,
  "count": 20,
  "offset": 0,
  "videos": [...]
}
```

### Delete Video

```
DELETE /api/v1/videos/{video_id}

Response (204): No Content
```

## 🛠️ Development

### Project Structure

```
autonomous-kids-shorts-generator/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── main.py
├── config.yaml
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   │
│   ├── core/
│   │   ├── generator.py
│   │   ├── script_engine.py
│   │   ├── video_composer.py
│   │   └── pipeline.py
│   │
│   ├── services/
│   │   ├── openai_service.py
│   │   ├── tts_service.py
│   │   ├── video_service.py
│   │   └── storage_service.py
│   │
│   ├── models/
│   │   ├── video.py
│   │   ├── script.py
│   │   └── project.py
│   │
│   ├── api/
│   │   ├── routes.py
│   │   ├── endpoints.py
│   │   └── schemas.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── helpers.py
│   │
│   └── content_safety/
│       ├── filter.py
│       └── validator.py
│
├── frontend/
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/
│   │   └── App.vue
│   └── dist/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── conftest.py
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
│
├── scripts/
│   ├── setup.sh
│   ├── train_model.py
│   └── benchmark.py
│
└── logs/
    └── app.log
```

### Setting Up Development Environment

```bash
# Install development tools
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/ tests/
black src/ tests/
isort src/ tests/

# Run type checking
mypy src/

# Run tests with coverage
pytest --cov=src tests/
```

### Code Style

- **Python**: PEP 8, Black formatter, 88-character line limit
- **JavaScript**: ESLint, Prettier
- **Type Hints**: Required for all Python functions
- **Docstrings**: Google-style docstrings for all classes and public methods

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_generator.py

# With coverage report
pytest --cov=src --cov-report=html

# Integration tests only
pytest tests/integration/

# E2E tests
pytest tests/e2e/ -v
```

### Writing Tests

```python
import pytest
from src.core.generator import VideoGenerator

class TestVideoGenerator:
    @pytest.fixture
    def generator(self):
        return VideoGenerator(api_key="test-key")
    
    def test_generate_video(self, generator):
        params = {"topic": "Test", "duration": 30}
        video = generator.generate(params)
        assert video.id is not None
        assert video.status == "processing"
    
    @pytest.mark.asyncio
    async def test_async_generation(self, generator):
        video = await generator.generate_async({"topic": "Test"})
        assert video is not None
```

## 🚀 Deployment

### Local Deployment

```bash
# Development server
python main.py

# Production server (with Gunicorn)
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Cloud Deployment (AWS Example)

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
docker tag kids-shorts:latest $ECR_REGISTRY/kids-shorts:latest
docker push $ECR_REGISTRY/kids-shorts:latest

# Deploy with ECS/Fargate
aws ecs update-service --cluster production --service kids-shorts --force-new-deployment
```

### Environment-Specific Configurations

- **Development**: `.env.development` - Local settings with debug enabled
- **Staging**: `.env.staging` - Pre-production validation
- **Production**: `.env.production` - Optimized for performance and security

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with clear, descriptive commits
4. **Write or update tests** as needed
5. **Ensure code passes linting** and type checks
6. **Create a Pull Request** with a clear description

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, perf, test, chore

Example:
```
feat(video-generation): add support for custom character selection

Allows users to select or create custom characters for generated videos.
Implements character database and selection UI.

Fixes #123
```

### Pull Request Process

1. Update README.md and documentation with changes
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Update CHANGELOG.md
5. Request reviews from maintainers
6. Merge once approved

## 🐛 Troubleshooting

### Common Issues

**Issue: "API key invalid" error**
```
Solution: Verify API key in .env file and ensure it has correct permissions
```

**Issue: Video generation times out**
```
Solution: 
- Increase MAX_WORKERS in .env
- Check available system memory
- Reduce video duration or quality settings
```

**Issue: Audio sync issues**
```
Solution:
- Update FFmpeg to latest version
- Check audio codec compatibility
- Adjust frame rate settings in config.yaml
```

**Issue: Docker container won't start**
```
Solution:
- Check Docker daemon is running
- Review logs: docker-compose logs
- Ensure ports 3000 and 8000 are available
- Verify .env file is properly configured
```

### Performance Optimization

```bash
# Enable GPU acceleration (CUDA)
export CUDA_VISIBLE_DEVICES=0

# Increase worker processes
export MAX_WORKERS=8

# Enable caching
redis-server &

# Monitor performance
python scripts/benchmark.py
```

### Getting Help

- **Issues**: Check [GitHub Issues](https://github.com/Rajkumarasam/autonomous-kids-shorts-generator/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/Rajkumarasam/autonomous-kids-shorts-generator/discussions)
- **Email**: contact@example.com
- **Documentation**: See [docs/](./docs/) folder

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [OpenAI GPT-4](https://openai.com/)
- Audio powered by [ElevenLabs](https://elevenlabs.io/)
- Video processing via [FFmpeg](https://ffmpeg.org/)
- Frontend framework: [React](https://react.dev/)
- Backend framework: [Flask](https://flask.palletsprojects.com/)

## 📞 Support

For support, please:

1. **Search existing documentation** at https://github.com/Rajkumarasam/autonomous-kids-shorts-generator/wiki
2. **Check open issues** at https://github.com/Rajkumarasam/autonomous-kids-shorts-generator/issues
3. **Contact maintainers** via email or GitHub discussions
4. **File a bug report** with reproduction steps and environment details

---

**Last Updated**: January 3, 2026

**Maintainer**: [@Rajkumarasam](https://github.com/Rajkumarasam)

**Status**: Active Development ✅
