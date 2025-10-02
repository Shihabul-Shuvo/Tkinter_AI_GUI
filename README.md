# Tkinter AI GUI Project

A professional desktop application built with Python Tkinter that provides an intuitive interface for AI-powered image captioning and sentiment analysis using Hugging Face transformer models.

## Features

### Core Functionality
- **Image-to-Text Captioning**: Generate descriptive captions for uploaded images using Vision Transformer (ViT) + GPT-2 model
- **Sentiment Analysis**: Analyze text sentiment with multilingual support (POSITIVE/NEGATIVE/NEUTRAL classification)
- **Drag & Drop Support**: Easy file handling with drag-and-drop interface for images
- **Real-time Processing**: Background threading ensures responsive UI during model inference
- **History Management**: Track and revisit previous analysis results
- **Cache Management**: Built-in Hugging Face model cache management with size monitoring

### User Interface Features
- **Modern GUI**: Clean, professional interface with themed widgets using ttk
- **Responsive Layout**: Adaptive layout that works on different screen sizes
- **Visual Feedback**: Progress indicators, status updates, and success animations
- **Interactive Elements**: Click-to-edit captions, expandable log panels, tooltips
- **Multi-panel Design**: Organized workspace with separate areas for input, output, and information
- **Accessibility**: Keyboard navigation support and screen reader friendly

### Technical Features
- **Local Processing**: Models run locally with automatic CPU/GPU detection
- **Performance Monitoring**: Built-in timing and performance tracking
- **Error Handling**: Comprehensive error management with detailed logging
- **Clipboard Integration**: Copy results and panel contents to clipboard
- **File Validation**: Input validation for image formats and file sizes
- **Settings Management**: Configurable cache directory and execution preferences

## Transformer Models Used

### 1. Image Captioning Model
- **Model ID**: `nlpconnect/vit-gpt2-image-captioning`
- **Architecture**: Vision Transformer (ViT) encoder + GPT-2 decoder
- **Task**: Image-to-text generation
- **Input**: PNG, JPG, JPEG, BMP images (up to 25MB)
- **Output**: Descriptive text captions
- **Use Case**: Automatic image description, accessibility, content indexing

### 2. Sentiment Analysis Model  
- **Model ID**: `tabularisai/multilingual-sentiment-analysis`
- **Architecture**: Multilingual transformer for text classification
- **Task**: Sentiment analysis with multilingual support
- **Input**: Text input (up to 3000 characters)
- **Output**: Sentiment labels (POSITIVE/NEGATIVE/NEUTRAL) with confidence scores
- **Use Case**: Text sentiment analysis, emotion detection, feedback analysis

## Implementation Overview

### Architecture Pattern
The application follows a **Model-View-Controller (MVC)** architecture:

- **Model Layer** (`app/models/`): Handles AI model integration and data processing
- **View Layer** (`app/views/`): Manages UI components and user interactions  
- **Controller Layer** (`app/controllers/`): Coordinates between models and views
- **Main Application** (`app/gui.py`): Central application management and navigation

### Key Implementation Features

#### Background Processing
- **Threading**: Model inference runs in daemon threads to prevent UI blocking
- **Callbacks**: Asynchronous result handling with error management
- **Progress Tracking**: Real-time status updates and progress indicators

#### Model Management
- **Lazy Loading**: Models are loaded only when first used
- **Device Detection**: Automatic CPU/GPU selection based on hardware availability
- **Caching**: Intelligent result caching to avoid redundant processing
- **Performance Monitoring**: Execution time tracking for optimization

#### Data Flow
1. User selects task (Image Captioning or Sentiment Analysis)
2. Input validation and preprocessing
3. Model controller spawns background thread
4. Model wrapper processes input using Hugging Face pipeline
5. Results are formatted and displayed in UI
6. Optional history saving and clipboard integration

## 🎯 OOP Concepts Implementation

This project demonstrates advanced Object-Oriented Programming concepts:

### 1. Multiple Inheritance
```python
class ImageCaptionWrapper(BaseModelWrapper, PreprocessMixin):
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Combines model management with image preprocessing capabilities
- **Benefits**: Code reuse and separation of concerns

### 2. Abstract Base Classes (ABC)
```python
class BaseModelWrapper(ABC, LoggingMixin):
    @abstractmethod
    def load(self): pass
    
    @abstractmethod  
    def process(self, data): pass
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Defines consistent interface for all model wrappers
- **Benefits**: Enforces implementation contracts and standardizes model integration

### 3. Method Decorators
```python
@timing
@simple_cache
def process(self, image_input):
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Performance monitoring and caching without modifying core logic
- **Benefits**: Clean separation of cross-cutting concerns

### 4. Encapsulation
- **Private Attributes**: `_model_name`, `_pipeline`, `_loaded`, `_last_time`
- **Controlled Access**: Public methods provide controlled access to internal state
- **Benefits**: Data integrity and controlled modification patterns

### 5. Polymorphism
- **Method Overriding**: Each model wrapper implements `process()` differently
- **Consistent Interface**: Same method signature with task-specific implementations
- **Benefits**: Uniform usage pattern across different model types

### 6. Mixins
```python
class LoggingMixin:
    def log(self, msg): pass

class PreprocessMixin:
    def pil_to_rgb(self, pil_image): pass
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Reusable functionality across multiple classes
- **Benefits**: Avoid code duplication and promote consistency

### 7. Composition
- **Model Controller**: Composes different model wrappers
- **View Components**: GUI components composed of multiple widgets
- **Benefits**: Flexible object relationships and modular design

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for model processing)
- **Storage**: At least 2GB free space for model cache
- **Network**: Internet connection for initial model downloads

### Python Dependencies
- `tkinter` - GUI framework (included with Python)
- `transformers>=4.30.0` - Hugging Face transformers library
- `torch>=2.0.0` - PyTorch for model inference
- `pillow>=9.0.0` - Image processing library
- `huggingface_hub>=0.15.0` - Model hub integration
- `pyperclip>=1.8.0` - Clipboard functionality
- `tkinterdnd2>=0.3.0` - Drag and drop support
- `ttkbootstrap>=1.10.0` - Enhanced tkinter themes

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Tkinter_AI_GUI_Project
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python verify_installation.py
```
This script checks all required packages and displays their status.

### 5. Run the Application
```bash
python main.py
```

## Usage Guide

### Getting Started
1. **Launch Application**: Run `python main.py`
2. **Select Task**: Choose between "Image to Text" or "Sentiment Analysis"
3. **Provide Input**: 
   - For images: Click "Choose Image", drag & drop, or use sample
   - For text: Type/paste text or use sample text
4. **Run Analysis**: Click "Run" button
5. **View Results**: Results appear in the center panel with additional details

### Navigation
- **🏠 Home**: Main interface for running AI tasks
- **📚 Models**: Information about the transformer models used
- **❓ Help**: Troubleshooting guide and common issues
- **⚙ Settings**: Configure cache directory and application settings

### Advanced Features
- **History**: Previous results are saved and accessible in the history panel
- **Cache Management**: Monitor and clear model cache from settings
- **Copy Results**: Use "Copy Result" to copy outputs to clipboard
- **Edit Captions**: Click on generated captions to edit them inline
- **Log Panel**: Click status bar to expand detailed logs

## Testing

### Run Individual Tests
```bash
# Test image captioning model
python tests/test_image_model.py

# Test sentiment analysis model  
python tests/test_text_model.py
```

### Test Sample Images
The project includes sample images in the `assets/` and `tests/` directories for testing image captioning functionality.

## Project Structure

```
Tkinter_AI_GUI_Project/
├── app/
│   ├── __init__.py
│   ├── gui.py                 # Main application window and navigation
│   ├── utils.py               # Shared utilities (ToolTip class)
│   ├── controllers/
│   │   └── model_controller.py # Threading and model coordination
│   ├── models/
│   │   └── hf_wrapper.py      # AI model wrappers with OOP concepts
│   ├── views/
│   │   └── home_view.py       # Main interface components
│   ├── help.md               # Help documentation
│   ├── model_info.md         # Model information
│   └── oop_docs.txt          # OOP concepts documentation
├── assets/
│   └── sample.jpg            # Sample image for testing
├── tests/
│   ├── test_image_model.py   # Image model tests
│   ├── test_text_model.py    # Text model tests
│   └── sample.jpg            # Test image
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── verify_installation.py   # Installation verification script
└── README.md                # This file
```

## Configuration

### Environment Variables
- `HF_HOME`: Set custom Hugging Face cache directory
  ```bash
  # Windows
  set HF_HOME=D:\hf_cache
  
  # macOS/Linux
  export HF_HOME=/path/to/cache
  ```

### Model Cache
- **Default Location**: `~/.cache/huggingface/hub`
- **Size**: Approximately 500MB-1GB per model
- **Management**: Use built-in cache management tools in Settings

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
**Problem**: Missing Python packages
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. tkinter Not Available
**Problem**: tkinter not included with Python installation
**Solution**: Install Python from python.org with tkinter support

#### 3. Model Download Failures
**Problem**: Network issues during model download
**Solution**: 
- Check internet connection
- Retry the operation
- Clear cache and try again

#### 4. Out of Memory Errors
**Problem**: Insufficient RAM for model processing
**Solution**:
- Close other applications
- Use smaller images
- Enable CPU-only processing

### Getting Help
1. Check the **Help** tab in the application for detailed troubleshooting
2. Review error logs in the expandable log panel
3. Use "Copy Panels" to share configuration details when seeking help

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Hugging Face** for the transformers library and pre-trained models
- **nlpconnect** for the ViT-GPT2 image captioning model
- **tabularisai** for the multilingual sentiment analysis model
- **Python Software Foundation** for the tkinter GUI framework

## Support

For questions, issues, or suggestions:
- Open an issue in the repository
- Check the built-in Help documentation
- Review the troubleshooting guide in the application

---

*Built with using Python, Tkinter, and Hugging Face Transformers*
