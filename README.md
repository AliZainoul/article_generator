# Article Generator

An AI-powered article generation tool that automatically creates well-structured, SEO-optimized HTML articles using AI models. The generator uses a two-step process: first creating a structured article plan, then generating detailed content for each section.

## Features

- **AI-Powered Content Generation**: Uses advanced AI models (DeepSeek R1 via OpenRouter or Google Gemini) to generate high-quality articles
- **Structured Planning**: Automatically creates article outlines before content generation
- **Content Validation**: Built-in validation to ensure article quality and consistency
- **HTML Output**: Generates fully formatted HTML articles with SEO metadata
- **Multi-Provider Support**: Supports OpenRouter and Google Gemini APIs
- **Colored Logging**: Enhanced logging with color-coded messages for better visibility
- **French Language Support**: Optimized for French content generation (extensible to other languages)

## Architecture

The Article Generator follows a modular architecture with the following components:

### Core Modules

1. **ArticlePlanner** (`article_generator/article_planner.py`)
   - Generates structured article plans/outlines
   - Creates a logical flow for the article content
   - Returns JSON format with sections and subsections

2. **ArticleWriter** (`article_generator/article_writer.py`)
   - Generates detailed content for each section
   - Expands the plan into full article text
   - Includes code examples and practical explanations

3. **ArticleValidator** (`article_generator/article_validator.py`)
   - Validates article quality and consistency
   - Ensures content meets quality standards
   - Provides validation feedback

4. **HTMLGenerator** (`article_generator/html_generator.py`)
   - Converts article content to HTML format
   - Applies the HTML template
   - Manages output file generation with timestamps

5. **Config** (`article_generator/config.py`)
   - Centralized configuration management
   - API provider settings (OpenRouter, Gemini)
   - Model selection and API credentials
   - Error handling utilities

6. **ColoredLogging** (`article_generator/colored_logging.py`)
   - Provides colored console output
   - Improves log readability

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/AliZainoul/article_generator.git
   cd article_generator
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root with your API credentials:

   ```bash
   # Default API provider (openrouter or gemini)
   API_PROVIDER=openrouter
   
   # OpenRouter Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # Google Gemini Configuration (if using Gemini)
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Basic Command

Generate an article with the following command:

```bash
python generate_article.py \
  --title "Your Article Title" \
  --topic "Main topic of the article" \
  --language "Programming language (e.g., Python, JavaScript)" \
  --provider openrouter
```

### Command Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--title` | Yes | The title of the article to generate | `"Les Classes en Python"` |
| `--topic` | Yes | The main topic or subject | `"Object-Oriented Programming"` |
| `--language` | Yes | Programming language for the article | `"Python"` |
| `--provider` | No | API provider to use (openrouter/gemini) | `openrouter` |

### Examples

#### Example 1: Generate a Python article

```bash
python generate_article.py \
  --title "Les Fonctions en Python" \
  --topic "Python Functions and Their Uses" \
  --language "Python"
```

#### Example 2: Generate an article using Gemini

```bash
python generate_article.py \
  --title "Introduction aux Design Patterns" \
  --topic "Software Design Patterns" \
  --language "Python" \
  --provider gemini
```

#### Example 3: Generate a JavaScript article

```bash
python generate_article.py \
  --title "Les Promesses en JavaScript" \
  --topic "Asynchronous JavaScript with Promises" \
  --language "JavaScript"
```

## Output

Generated articles are saved as HTML files in the `articles/` directory with the following naming convention:

```bash
YYYY-MM-DD-article-title-slug.html
```

**Example output:**

- `2025-03-23-les-fonctions-en-python.html`
- `2025-03-23-les-classes-en-poo.html`

The HTML files include:

- Proper SEO metadata
- Open Graph tags for social sharing
- Structured content with sections and subsections
- Code examples with syntax highlighting
- Professional styling

## Project Structure

```bash
article_generator/
├── generate_article.py           # Main entry point
├── requirements.txt              # Python dependencies
├── _template_article.html        # HTML template for articles
├── README.md                     # This file
├── article_generator/
│   ├── __init__.py
│   ├── article_planner.py        # Article outline generation
│   ├── article_writer.py         # Content generation
│   ├── article_validator.py      # Content validation
│   ├── html_generator.py         # HTML file generation
│   ├── colored_logging.py        # Enhanced logging
│   └── config.py                 # Configuration management
├── articles/                     # Output directory for generated HTML files
└── output/                       # Plan files (intermediate outputs)
```

## Dependencies

The project uses the following main dependencies:

- **openai** (1.65.4) - OpenAI Python SDK (for API communication)
- **python-dotenv** (1.0.1) - Environment variable management
- **pydantic** (2.10.6) - Data validation and settings
- **httpx** (0.28.1) - HTTP client
- **tqdm** (4.67.1) - Progress bars
- **pytest** (8.3.5) - Testing framework

See `requirements.txt` for the complete list of dependencies.

## API Providers

### OpenRouter

OpenRouter provides access to multiple AI models through a single API:

- **Model used**: DeepSeek R1 (`deepseek/deepseek-r1:free`)
- **Advantages**: Free tier available, multiple model options
- **Setup**: Get your API key from [openrouter.ai](https://openrouter.ai)

### Google Gemini

Google's AI model for content generation:

- **Model used**: Gemini 2.0 Flash (`gemini-2.0-flash`)
- **Setup**: Get your API key from [Google AI Studio](https://aistudio.google.com)

## Configuration Details

### Model Selection

Edit `article_generator/config.py` to change which AI models are used for each task:

```python
ARTICLE_PLANNER_MODELS = {
    'openrouter': ["deepseek/deepseek-r1:free"],
    'gemini': ["gemini-2.0-flash"]
}

ARTICLE_WRITER_MODELS = {
    'openrouter': ["deepseek/deepseek-r1:free"],
    'gemini': ["gemini-2.0-flash"]
}
```

### Template Customization

The HTML template is stored in `_template_article.html`. You can customize:

- Styling and CSS classes
- Metadata structure
- SEO elements
- Layout and sections

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

```bash
Error: OPENROUTER_API_KEY not found
```

**Solution**: Ensure your `.env` file contains the correct API key:

```bash
OPENROUTER_API_KEY=your_key_here
```

#### 2. Configuration Error

```bash
Error: Configuration error: Invalid API provider
```

**Solution**: Ensure the `--provider` argument is either `openrouter` or `gemini`.

#### 3. Missing Dependencies

```bash
ModuleNotFoundError: No module named 'openai'
```

**Solution**: Install dependencies:

```bash
pip install -r requirements.txt
```

#### 4. Output Directory Error

```bash
Error: Permission denied creating articles directory
```

**Solution**: Ensure the project directory has write permissions:

```bash
chmod -R 755 /path/to/article_generator
```

## Workflow

The article generation process follows these steps:

```bash
1. Parse Command Arguments
   ↓
2. Generate Article Plan
   - Create structured outline with sections
   - Define content hierarchy
   ↓
3. Generate Article Content
   - Write detailed content for each section
   - Add examples and explanations
   - Validate content quality
   ↓
4. Create HTML Article
   - Apply HTML template
   - Add metadata and SEO tags
   - Save to articles/ directory
   ↓
5. Output
   - HTML file ready for publication
```

## Testing

To run tests (if configured):

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add improvement'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is maintained by [AliZainoul](https://github.com/AliZainoul).

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## Notes

- The first request to an AI provider may take longer as the models initialize
- Ensure you have sufficient API credits/quota with your chosen provider
- Generated articles are in French by default but can be configured for other languages
- All generated HTML files include timestamps for easy organization

---

**Last Updated**: December 23, 2025
