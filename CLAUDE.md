# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **multi-functional AI workspace** designed for beginners and non-technical users, organized into numbered folders for different AI-powered tasks. The system integrates multiple AI services and automation tools to provide comprehensive image analysis, web scraping, and AI agent development capabilities.

### Key Technologies
- **Primary Language**: Python 3.x (28 Python files)
- **Web Automation**: Playwright via Chrome MCP
- **AI Services**: SiliconFlow API, OpenAI integration
- **Dependencies**: Node.js for Playwright, Python packages for AI services

## Core Working Principles

### 🚫 Strict Data Authenticity Policy
- **NEVER fabricate data**: Do not create fake research results, pretend to access websites, or generate fictional statistics
- **NEVER guess answers**: If information cannot be obtained, explicitly state the limitation
- **NEVER hide limitations**: Clearly communicate what can and cannot be done
- **ALWAYS be truthful**: Provide honest assessment of capabilities and limitations

### ✅ Required Response Protocol
When encountering these situations, respond directly:
```
❌ Cannot access specific website → Explain technical limitation
❌ Cannot obtain real-time data → State data availability constraints  
❌ Cannot read local files → Request explicit permission
❌ Cannot connect to services → Describe connection issues

Instead, provide:
✅ Clear explanation of technical limitations
✅ Alternative solution suggestions
✅ Guidance for manual data acquisition
✅ Honest capability assessment
```

### 📁 Folder Management Standards
This workspace follows strict folder organization:

- **01_image_recognition/** - Image analysis and recognition tools
- **02_chrome_mcp/** - Chrome automation and web scraping  
- **03_claude_code/** - Claude configuration and documentation
- **04_silicon_flow/** - Silicon Flow AI service integration
- **05_ai_agent/** - AI agent development and management
- **06_config_data/** - Configuration files and sensitive data
- **07_archive/** - Completed projects and archival files
- **08_temp/** - Temporary files (clean regularly)
- **09_resources/** - Shared resources and templates

**File Organization Rules**:
- Source code → Corresponding project folder
- Configuration files → 06_config_data/
- Documentation → Related project folder or root
- Temporary files → 08_temp/ with regular cleanup
- Shared resources → 09_resources/

## Common Development Commands

### Image Analysis System (01_image_recognition/)
```bash
# Main system commands
python3 image_analysis_system.py status
python3 image_analysis_system.py analyze image.jpg
python3 image_analysis_system.py analyze-dir ./images
python3 image_analysis_system.py monitor --dirs pic uploads
python3 image_analysis_system.py interactive

# Individual component testing
python3 automated_image_analyzer.py
python3 image_upload_monitor.py
python3 image_analysis_api.py
```

### Chrome MCP System (02_chrome_mcp/)
```bash
# Page analysis
python3 chrome_page_analyzer.py <URL>
python3 chrome_content_extractor.py <URL>
python3 chrome_tab_analyzer.py <URL>

# Playwright setup (if needed)
npx playwright install
```

### Silicon Flow Integration (04_silicon_flow/)
```bash
# Setup and testing
python3 setup_siliconflow.py
python3 simple_api_test.py
```

### AI Agent System (05_ai_agent/)
```bash
# Agent management
python3 agent_controller.py
python3 humanoid_agent.py
python3 global_memory_manager.py
```

## Architecture Overview

### Modular Folder Structure
Each numbered folder represents a self-contained module with specific responsibilities:

**01_image_recognition/** - Core image analysis system
- `image_analysis_system.py` - Main system orchestrator
- `automated_image_analyzer.py` - Multi-model AI analysis engine
- `image_upload_monitor.py` - File system monitoring
- `image_analysis_api.py` - REST API interface
- `global_memory_manager.py` - Cross-session memory and learning

**02_chrome_mcp/** - Web automation and content extraction
- `chrome_page_analyzer.py` - Main page analysis orchestrator
- `chrome_content_extractor.py` - Structured content extraction
- `chrome_tab_analyzer.py` - Tab management and analysis

**05_ai_agent/** - Intelligent agent development
- `humanoid_agent.py` - Human-like agent interface
- `agent_controller.py` - Agent lifecycle management
- `global_memory_manager.py` - Shared memory system (cross-module)

### Key Architectural Patterns

**Memory Management System**
- Global memory persists across sessions in `.memory/` directory
- User preference learning and adaptation
- Analysis history tracking and pattern recognition
- Automated backup and recovery mechanisms

**API Integration Pattern**
- Standardized API interface across all modules
- Error handling with retry mechanisms
- Multi-model support (SiliconFlow, OpenAI, etc.)
- Configuration-driven model selection

**Automation-First Design**
- File system monitoring for automatic processing
- Event-driven architecture
- Background task processing
- Status persistence and recovery

## Configuration Management

### Environment Variables (.env)
```bash
SILICONFLOW_API_KEY=your_api_key_here
DEFAULT_MODEL=Qwen/Qwen2.5-VL-72B-Instruct
OPENAI_API_KEY=your_openai_key (optional)
```

### System Configuration (image_analyzer_config.json)
```json
{
  "auto_analyze": true,
  "auto_watch": true,
  "default_model": "Qwen/Qwen2.5-VL-72B-Instruct",
  "analysis_types": {
    "wechat": true,
    "table": true,
    "general": true,
    "weather": true
  },
  "output_formats": ["json", "txt"],
  "save_history": true,
  "max_history_size": 100
}
```

### Memory System Structure
```
.memory/
├── config.json          # System configuration
├── context.pkl          # Runtime context data
├── history.json         # Analysis history
├── preferences.json     # User preferences
└── backup_YYYYMMDD_HHMMSS/  # Automatic backups
```

## Development Workflow

### Adding New Analysis Types
1. Create analysis function in `automated_image_analyzer.py`
2. Add type detection logic in `image_analysis_system.py`
3. Update configuration schema in `image_analyzer_config.json`
4. Add tests and documentation

### Working with the Memory System
```python
from global_memory_manager import GlobalMemoryManager

# Initialize memory manager
memory = GlobalMemoryManager()

# Store analysis results
memory.store_analysis_result(image_path, result, analysis_type)

# Learn user preferences
memory.learn_preference(analysis_type, model_used, user_feedback)

# Get context-aware suggestions
suggestions = memory.get_context_suggestions(current_task)
```

### Chrome MCP Integration
```python
from chrome_page_analyzer import ChromePageAnalyzer

# Analyze webpage
analyzer = ChromePageAnalyzer()
result = analyzer.analyze_page(url)

# Extract structured content
content = analyzer.extract_content(url, content_type)

# Monitor page changes
changes = analyzer.monitor_page(url, interval=60)
```

## Data Flow Patterns

### Image Analysis Pipeline
1. **Input Detection** → Monitor detects new files in specified directories
2. **Type Classification** → System determines analysis type based on filename/content
3. **Model Selection** → Chooses optimal AI model based on analysis type
4. **Analysis Execution** → Processes image through selected AI service
5. **Result Storage** → Saves structured results with metadata
6. **Learning Phase** → Updates user preferences and system memory

### Web Analysis Pipeline
1. **URL Processing** → Chrome MCP loads and renders page
2. **Content Extraction** → Extracts text, links, images, structured data
3. **Analysis Engine** → Performs SEO, accessibility, content analysis
4. **Result Formatting** → Generates structured reports and recommendations
5. **Change Detection** → Monitors for page updates over time

## File Organization Principles

### Folder Naming Convention
- Use numeric prefixes (01_, 02_, etc.) for logical ordering
- Keep folders as self-contained modules
- Shared resources go in `09_resources/`
- Configuration files centralized in `06_config_data/`

### File Naming Standards
- Python files: lowercase_with_underscores.py
- Configuration files: descriptive_name.json
- Documentation: README.md, descriptive_name.md
- Test files: test_descriptive_name.py

### Cross-Module Dependencies
- Shared utilities go in `09_resources/`
- Common configuration in `06_config_data/`
- Memory system shared across modules
- Avoid circular dependencies between numbered folders

## Error Handling and Debugging

### Common Issues and Solutions
1. **API Key Issues** → Check `.env` file and API key validity
2. **Network Problems** → Verify internet connectivity and API service status
3. **Memory Corruption** → Delete `.memory/` directory to reset
4. **Permission Issues** → Ensure file system permissions for target directories
5. **Model Failures** → Check model availability and API quotas

### Debug Commands
```bash
# Check system status
python3 image_analysis_system.py status

# View memory state
python3 image_analysis_system.py memory

# Clear corrupted memory
python3 image_analysis_system.py clear

# Run diagnostics
python3 image_analysis_system.py diagnose
```

## Testing and Quality Assurance

### Image Analysis Testing
- Test with various image formats (JPG, PNG, GIF, etc.)
- Verify different analysis types (weather, table, wechat, general)
- Test file monitoring and automatic processing
- Validate memory persistence across sessions

### Web Analysis Testing
- Test with different website types and structures
- Verify content extraction accuracy
- Test change detection functionality
- Validate performance with large pages

### Integration Testing
- Test cross-module communication
- Verify shared memory system
- Test configuration management
- Validate error handling across modules

## Performance Considerations

### Memory Management
- Regular cleanup of historical data
- Configurable memory limits
- Automatic backup and compression
- Efficient data structures for large datasets

### API Optimization
- Connection pooling for API calls
- Caching of frequently accessed data
- Rate limiting and retry logic
- Fallback model selection

### File System Optimization
- Efficient file monitoring algorithms
- Configurable scan intervals
- Batch processing for multiple files
- Proper handling of large files

## Security and Privacy

### API Key Management
- Store sensitive keys in `.env` files (never in code)
- Regular rotation of API keys
- Usage monitoring and quota management
- Key revocation procedures

### Data Privacy
- Local processing of sensitive images when possible
- Secure storage of analysis results
- User control over data retention
- Compliance with data protection regulations

### File System Security
- Proper permission management
- Secure handling of uploaded files
- Audit logging for sensitive operations
- Regular security updates

## Extension and Customization

### Adding New AI Models
1. Update model configuration in `image_analyzer_config.json`
2. Add model-specific logic in analysis modules
3. Update model selection algorithms
4. Add model performance monitoring

### Creating New Analysis Types
1. Define analysis type in configuration schema
2. Implement type-specific analysis logic
3. Add result formatting and storage
4. Update user interface and documentation

### Integrating New AI Services
1. Create service-specific configuration
2. Implement service adapter classes
3. Add error handling and retry logic
4. Update service monitoring and logging

## Deployment and Operations

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd 06_config_data && npm install

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Backup and Recovery
- Regular backups of `.memory/` directory
- Configuration file versioning
- Database export/import functionality
- Disaster recovery procedures

### Monitoring and Maintenance
- System health monitoring
- API usage tracking
- Performance metrics collection
- Automated cleanup and maintenance tasks