
# Scholar Hunter 🎓📚
<div align="center">
  <a href="README.md">English</a> | <a href="README_zh.md">中文</a>
</div>
Scholar Hunter is a powerful Python script designed to help users retrieve Google Scholar profile links and citation information based on the scholar's name and organization. This tool enables researchers and academic institutions to efficiently collect and manage academic data.

## Features 🌟

1. **Initial Search**: Find Google Scholar profile links based on the scholar's name and organization, quickly locating the target scholar.
2. **Detailed Search**: Retrieve detailed citation information from the Google Scholar profile, including published papers and citation counts.
3. **Concurrent Processing**: Supports multi-threaded concurrent searches, significantly improving data retrieval efficiency.
4. **Flexible Configuration**: Detailed configuration through the `config.yaml` file to meet the needs of different users.

### Installation Instructions 📦

1. **Ensure you have Python 3.7 or higher installed**.
2. **Clone the project repository**:
   ```bash
   git clone https://github.com/Shangliyuan/scholar-hunter.git
   cd scholar-hunter
   ```
3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the `config.yaml` file**: Adjust the settings according to your needs.

## Configuration 🛠️

Before running the script, you need to set up the `config.yaml` file:

```yaml
webdriver:
  path: 'path/to/chromedriver'  # Path to the chromedriver executable
  chrome_binary_path: 'path/to/chrome'  # Path to the Chrome browser executable

files:
  input: 'data.csv'  # Input file containing scholar information
  output_initial: 'search_results.csv'  # Output file for initial search results
  output_details: 'citation_search_results.csv'  # Output file for detailed citation information
  error_log: 'google_scholar_search_errors.log'  # Log file for error messages

search:
  max_workers: 10  # Maximum number of concurrent search threads

logging:
  level: ERROR  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  format: '%(asctime)s - %(levelname)s - %(message)s'  # Log message format

columns:
  id: 'id'  # Column name for the unique identifier
  name: 'name'  # Column name for the scholar's name
  organization: 'organization'  # Column name for the scholar's organization (optional)
```

## Input Data Format 📝

Prepare a CSV file (e.g., `data.csv`) containing the following columns as input data:

- id: Unique identifier for each scholar
- name: Scholar's name
- organization: Scholar's organization (optional)

Example:

| id  | name              | organization                          |
|-----|-------------------|---------------------------------------|
| 440 | Cristina Arellano | Federal Reserve Bank of Minneapolis   |
| 441 | Juanna S. Joensen | University of Chicago                 |

## Usage 🚀

1. **Initial Search**:
   ```
   python scholar_hunter.py --mode initial
   ```
   This will generate a `search_results.csv` file containing Google Scholar profile links.

2. **Detailed Search**:
   ```
   python scholar_hunter.py --mode details
   ```
   This will generate a `citation_search_results.csv` file containing detailed citation information.

## Output 📊

1. `search_results.csv`: Contains Google Scholar profile links for each scholar.
2. `citation_search_results.csv`: Contains detailed citation information for each scholar.

### Frequently Asked Questions 🤔

- **Q: I encountered a `chromedriver` path error, what should I do?**
  - A: Ensure you have downloaded the `chromedriver` that matches your Chrome browser version. You can resolve this issue by following these steps:
    1. Visit the [ChromeDriver download page](https://developer.chrome.com/docs/chromedriver/downloads) and download the matching version of `chromedriver` and `chrome`.
    2. After downloading, unzip the file to your chosen directory.
    3. In the `config.yaml` file, set the paths for `chromedriver` and `chrome` to the unzipped file paths. For example:
       ```yaml
       webdriver:
         path: 'D:\chromeCrawl\122.0.6261.69\chromedriver-win64\chromedriver.exe'
         chrome_binary_path: 'D:\chromeCrawl\122.0.6261.69\chrome-win64\chrome.exe'
       ```
    4. **Ensure `chromedriver` is executable**: On some systems, you may need to grant `chromedriver` executable permissions. You can do this by running:
       ```bash
       chmod +x /path/to/chromedriver
       chmod +x /path/to/chrome
       ```
- **Q: How do I handle errors in concurrent searches?**
  - A: You can adjust the `max_workers` value in the `config.yaml` file to reduce the number of concurrent threads, or check the `error_log` file for error messages to troubleshoot.

