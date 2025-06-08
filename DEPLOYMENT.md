# Deployment Guide - Advanced RAG YouTube Transcript Chat AI

This guide provides comprehensive deployment instructions for the industry-standard RAG implementation.

## Quick Start Deployment

### Local Development Setup

1. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file with your credentials
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Install Dependencies**
   ```bash
   # Install from full requirements
   pip install -r requirements-full.txt
   
   # Or install core dependencies only
   pip install streamlit openai langchain langchain-community langchain-openai faiss-cpu sqlalchemy psycopg2-binary reportlab youtube-transcript-api requests python-dotenv
   ```

3. **Launch Application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. **Access Interface**
   Open `http://localhost:5000` in your browser

## Production Deployment

### Cloud Platform Deployment

#### Replit Deployment (Recommended)
- Automatic dependency management
- Built-in PostgreSQL database
- Zero-configuration deployment
- Environment variable management

#### Heroku Deployment
```bash
# Create Heroku app
heroku create youtube-transcript-ai

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
```

#### AWS Deployment
```bash
# Using AWS App Runner or ECS
# Configure environment variables in AWS Console
# Set up RDS PostgreSQL instance
# Deploy container with proper IAM roles
```

### Docker Deployment

```dockerfile
# Dockerfile included in project
FROM python:3.11-slim

WORKDIR /app
COPY requirements-full.txt .
RUN pip install -r requirements-full.txt

COPY . .
EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t youtube-transcript-ai .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key youtube-transcript-ai
```

## Environment Variables

### Required Configuration
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database Configuration (optional - defaults to SQLite)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Advanced RAG Configuration (Optional)
```bash
# RAG System Tuning
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=200
RAG_EMBEDDING_MODEL=text-embedding-3-large
RAG_CHAT_MODEL=gpt-4o
RAG_TEMPERATURE=0.1
RAG_MAX_TOKENS=1000

# Quality Thresholds
MIN_CHUNKS_THRESHOLD=10
LOW_FAITHFULNESS_THRESHOLD=0.7

# Performance Settings
BATCH_SIZE=50
SIMILARITY_SEARCH_K=8
RERANK_TOP_K=6
```

## Database Setup

### PostgreSQL Configuration
```sql
-- Create database
CREATE DATABASE youtube_transcript_ai;

-- Create user with permissions
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE youtube_transcript_ai TO app_user;

-- Tables are created automatically by SQLAlchemy
```

### SQLite (Development)
```bash
# SQLite database created automatically
# Location: ./youtube_transcripts.db
# No additional setup required
```

## Performance Optimization

### System Requirements
```bash
# Minimum Requirements
CPU: 2 cores
RAM: 4GB
Storage: 10GB SSD

# Recommended Production
CPU: 4+ cores
RAM: 8GB+
Storage: 50GB+ SSD
Network: High bandwidth for OpenAI API calls
```

### Scaling Configuration
```bash
# Streamlit Configuration (.streamlit/config.toml)
[server]
headless = true
address = "0.0.0.0"
port = 5000
maxUploadSize = 200

[browser]
gatherUsageStats = false

# Performance Tuning
[theme]
base = "dark"
primaryColor = "#FF6B6B"
```

## Monitoring and Logging

### Application Monitoring
```python
# Built-in monitoring features
- Response quality evaluation
- Processing time tracking
- Error rate monitoring
- User interaction analytics
```

### Log Configuration
```bash
# Environment variables for logging
LOG_LEVEL=INFO
ENABLE_DEBUG_LOGGING=false
LOG_FORMAT=json

# Streamlit logging
export STREAMLIT_LOGGER_LEVEL=INFO
```

## Security Configuration

### API Security
```bash
# Rate limiting (if using reverse proxy)
# Nginx configuration example
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location / {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://localhost:5000;
}
```

### HTTPS Configuration
```bash
# Let's Encrypt SSL certificate
certbot --nginx -d yourdomain.com

# Or use cloud provider SSL termination
# AWS ALB, Cloudflare, etc.
```

## Troubleshooting

### Common Issues

#### OpenAI API Issues
```bash
# Check API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Verify rate limits and quota
# Monitor usage in OpenAI dashboard
```

#### Database Connection Issues
```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT version();"

# Check SQLAlchemy connection
python -c "from backend.database import DatabaseManager; db = DatabaseManager(); print('Connection successful')"
```

#### Memory Issues
```bash
# Monitor memory usage
ps aux | grep streamlit
htop

# Optimize chunk processing
# Reduce batch size in environment variables
BATCH_SIZE=25
```

### Performance Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Monitor API response times
# Check OpenAI API status
# Verify database query performance
```

## Backup and Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20240101.sql
```

### Application Data
```bash
# Backup embeddings and transcripts
# Data is stored in database
# Regular database backups sufficient
```

## Upgrade Process

### Version Updates
```bash
# Update dependencies
pip install -r requirements-full.txt --upgrade

# Database migrations (if any)
# Automatic schema updates handled by SQLAlchemy

# Restart application
# Streamlit auto-reloads on file changes
```

### RAG System Upgrades
```bash
# Advanced RAG improvements are backward compatible
# Existing embeddings automatically upgraded
# Quality monitoring triggers regeneration as needed
```

## Cost Optimization

### OpenAI API Usage
```bash
# Monitor costs in OpenAI dashboard
# Optimize embedding generation frequency
# Use caching for repeated queries
# Consider batch processing for multiple videos
```

### Infrastructure Costs
```bash
# Use appropriate instance sizes
# Scale down during low usage
# Implement auto-scaling policies
# Monitor database storage growth
```

## Support and Maintenance

### Regular Maintenance
```bash
# Weekly tasks
- Monitor application performance
- Check error logs
- Verify API quota usage
- Update dependencies if needed

# Monthly tasks
- Database cleanup of old embeddings
- Performance optimization review
- Security updates
- Backup verification
```

### Getting Help
```bash
# Check logs for errors
tail -f /var/log/streamlit.log

# Review application metrics
# Monitor database performance
# Check OpenAI API status

# Documentation
- README.md - General overview
- API_DOCUMENTATION.md - Technical reference
- ADVANCED_FEATURES.md - RAG architecture details
```