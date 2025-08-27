# 🎬 ScrapeTube CC - Thai YouTube Subtitles Scraper

> 🌟 **Part of the Mangosteen Dataset Project** 🥭  

## ⚠️ Important Notice

🚨 **This code is for research and educational purposes only** - not intended for production use!  
🔧 There are several sub-optimal points in the codebase <br>
🤝 **We welcome seasonal contributors!** Feel free to contribute and help make this project better

## 🚀 Quick Start

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd scrapetube_cc

# Set environment variables
PYTHONPATH=<path-to-project>
LOG_LEVEL=INFO
LOGURU_LEVEL=INFO
```

### 2. Create Required Directories
```bash
mkdir -p data logs
```

### 3. Install Dependencies with UV
We use [uv](https://github.com/astral-sh/uv) for fast Python package management:

```bash
# Install uv if you haven't already. 
# Refer to https://docs.astral.sh/uv/getting-started/installation/

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies
uv sync --group dev
```

If you prefer using your own virtual environment, install dependencies from `requirements.txt`

## 📚 Usage Examples

We provide comprehensive Jupyter notebooks demonstrating all functionality:

| Notebook | Description | Purpose |
|----------|-------------|---------|
| `nb_00_get_video_meta.ipynb` | **Video Metadata Extraction** | How to search and extract video metadata |
| `nb_01_get_subtitles.ipynb` | **Subtitle Downloading** | Download Thai subtitles from Creative Commons videos |
| `nb_02_process_subtitles.ipynb` | **Text Processing** | Process and normalize subtitle text for datasets |

## 🌐 Proxy Configuration

**🔒 Highly Recommended**: Use rotating proxy services to avoid YouTube rate limiting

```python
# Example proxy configuration
proxies = {
    'http': 'http://username:password@proxy-server:port',
    'https': 'http://username:password@proxy-server:port'
}
```

**Recommended Services:**
- 🔄 [WebShare Rotating Residential Proxies](https://www.webshare.io/)
- 🏢 Other residential proxy providers

## 🛠️ Core Technologies

This project leverages several powerful Python libraries:

| Library | Purpose | Link |
|---------|---------|------|
| 🔍 **scrapetube** | YouTube scraping foundation | [GitHub](https://github.com/dermasmid/scrapetube/tree/master) |
| 📝 **youtube-transcript-api** | Subtitle extraction | [GitHub](https://github.com/jdepoix/youtube-transcript-api) |
| 🎥 **yt-dlp** | Video metadata and license checking | [GitHub](https://github.com/yt-dlp/yt-dlp) | 


# Scrapetube (Original ReadMe)
This module will help you scrape youtube without the official youtube api and without selenium.

With this module you can:


* Get all videos from a Youtube channel.
* Get all videos from a playlist.
* Search youtube.

# Installation

```bash
pip3 install scrapetube
```

# Usage
Here's a few short code examples.

## Get all videos for a channel
```python
import scrapetube

videos = scrapetube.get_channel("UCCezIgC97PvUuR4_gbFUs5g")

for video in videos:
    print(video['videoId'])
```

## Get all videos for a playlist
```python
import scrapetube

videos = scrapetube.get_playlist("PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU")

for video in videos:
    print(video['videoId'])
```

## Make a search
```python
import scrapetube

videos = scrapetube.get_search("python")

for video in videos:
    print(video['videoId'])
```

# Full Documentation

[https://scrapetube.readthedocs.io/en/latest/](https://scrapetube.readthedocs.io/en/latest/)
