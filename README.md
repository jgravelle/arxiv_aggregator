# arXiv Research Aggregator

A Python-based web application that automatically fetches, processes, and publishes the latest research papers from arXiv across multiple computer science domains including AI, Machine Learning, Computer Vision, Robotics, and Cryptography/Security.

## Features

- **Multi-Domain Coverage**: Aggregates papers from CS.AI, CS.LG, CS.CV, CS.RO, and CS.CR categories
- **AI-Powered Content Enhancement**: Uses Ollama LLM to rewrite titles and generate engaging summaries
- **Visual Content Generation**: Automatically generates relevant images using Unsplash API
- **Featured Article Selection**: Intelligent scoring system to highlight the most interesting papers
- **Automated Publishing**: Direct FTP upload to web server for seamless deployment
- **Responsive Web Interface**: Clean, modern HTML templates for optimal viewing experience
- **Duplicate Prevention**: Tracks processed papers to avoid republishing

## Architecture

```
arxiv_aggregator/
├── aggregator.py           # Main AI aggregator
├── aggregator_ml.py        # Machine Learning aggregator
├── aggregator_cv.py        # Computer Vision aggregator
├── aggregator_ro.py        # Robotics aggregator
├── aggregator_cr.py        # Cryptography/Security aggregator
├── aggregator_hc.py        # Human-Computer Interaction aggregator
├── config.py              # Configuration management
├── content_utils.py       # Content processing utilities
├── featured_tracker.py    # Featured article selection logic
├── generate_html.py       # HTML generation utilities
├── run_all_aggregators.py # Orchestration script
├── templates/             # HTML templates
│   ├── base_template.html
│   ├── ml_template.html
│   ├── cv_template.html
│   ├── ro_template.html
│   └── cr_template.html
└── output/               # Generated HTML files and images
```

## Prerequisites

- **Python 3.8+**
- **Ollama** (for AI content generation)
  - Install from [ollama.ai](https://ollama.ai)
  - Pull required models: `ollama pull llama3.1:8b` and `ollama pull llava:latest`
- **FTP Server Access** (for publishing)
- **Unsplash API Account** (for image generation)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jgravelle/arxiv_aggregator.git
   cd arxiv_aggregator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual credentials:
   ```env
   # FTP Configuration
   FTP_HOST=your-ftp-host.com
   FTP_USER=your-ftp-username
   FTP_PASS=your-ftp-password
   FTP_REMOTE_DIR=.

   # Unsplash API (get from https://unsplash.com/developers)
   UNSPLASH_ACCESS_KEY=your-access-key
   UNSPLASH_SECRET_KEY=your-secret-key
   UNSPLASH_APPLICATION_ID=your-app-id

   # Ollama Configuration (optional, defaults provided)
   OLLAMA_MODEL=llama3.1:8b
   OLLAMA_VISION_MODEL=llava:latest
   ```

4. **Start Ollama service**:
   ```bash
   ollama serve
   ```

## Usage

### Run All Aggregators
Process all research domains and publish to web:
```bash
python run_all_aggregators.py
```

### Run Individual Aggregators
Process specific research domains:
```bash
python aggregator.py      # AI papers
python aggregator_ml.py   # Machine Learning papers
python aggregator_cv.py   # Computer Vision papers
python aggregator_ro.py   # Robotics papers
python aggregator_cr.py   # Cryptography/Security papers
```

### Local Development
Generate HTML files without FTP upload:
```bash
python aggregator.py --no-upload
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FTP_HOST` | FTP server hostname | Yes |
| `FTP_USER` | FTP username | Yes |
| `FTP_PASS` | FTP password | Yes |
| `FTP_REMOTE_DIR` | Remote directory path | No (default: ".") |
| `UNSPLASH_ACCESS_KEY` | Unsplash API access key | Yes |
| `UNSPLASH_SECRET_KEY` | Unsplash API secret key | Yes |
| `UNSPLASH_APPLICATION_ID` | Unsplash application ID | Yes |
| `OLLAMA_MODEL` | Ollama text model | No (default: "llama3.1:8b") |
| `OLLAMA_VISION_MODEL` | Ollama vision model | No (default: "llava:latest") |

### Customization

- **Paper Limits**: Modify `MAX_ARTICLES` in aggregator files
- **Categories**: Update arXiv API URLs in `config.py`
- **Templates**: Customize HTML templates in `templates/` directory
- **Scoring Logic**: Adjust featured article selection in `featured_tracker.py`

## API Integration

### arXiv API
- Fetches recent papers using arXiv's Atom feed API
- Supports category-specific queries
- Handles pagination and rate limiting

### Ollama Integration
- **Text Generation**: Rewrites titles and creates engaging summaries
- **Content Scoring**: Evaluates paper relevance and interest level
- **Local Processing**: All AI operations run locally for privacy

### Unsplash API
- Generates contextually relevant images for each paper
- Implements search keyword optimization
- Handles API rate limits and fallbacks

## Output Structure

Generated files are organized as follows:
```
output/
├── index.html          # Main landing page
├── ml.html            # Machine Learning papers
├── cv.html            # Computer Vision papers
├── ro.html            # Robotics papers
├── cr.html            # Cryptography papers
└── images/            # Generated article images
    ├── article_[hash].jpg
    └── ...
```

## Automation

### Scheduled Execution
Set up automated runs using cron (Linux/macOS) or Task Scheduler (Windows):

```bash
# Run every 6 hours
0 */6 * * * cd /path/to/arxiv_aggregator && python run_all_aggregators.py
```

### CI/CD Integration
The project can be integrated with GitHub Actions or similar CI/CD platforms for automated deployment.

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   - Ensure Ollama is running: `ollama serve`
   - Check if models are installed: `ollama list`

2. **FTP Upload Failures**:
   - Verify FTP credentials in `.env`
   - Check network connectivity and firewall settings

3. **Unsplash API Limits**:
   - Monitor API usage in Unsplash dashboard
   - Implement caching for frequently used images

4. **Missing Dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Debug Mode
Enable verbose logging by setting environment variable:
```bash
export DEBUG=1
python aggregator.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling for external API calls
- Test with multiple paper categories
- Update documentation for new features

## Security

- **Environment Variables**: Never commit `.env` file to version control
- **API Keys**: Rotate keys regularly and use least-privilege access
- **FTP Credentials**: Use secure FTP (SFTP) when possible
- **Input Validation**: All external data is sanitized before processing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [arXiv](https://arxiv.org/) for providing open access to research papers
- [Ollama](https://ollama.ai/) for local AI model hosting
- [Unsplash](https://unsplash.com/) for high-quality stock photography
- The open-source community for various Python libraries used

## Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Note**: This tool is designed for educational and research purposes. Please respect arXiv's terms of service and API rate limits.
