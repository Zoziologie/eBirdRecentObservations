# eBird Recent Observations

Discover and explore recent bird observations in your region with intelligent rarity scoring. This interactive web application helps birders find rare and interesting species by analyzing eBird data and providing frequency-based rarity assessments for recent sightings.

## Features

- 🦅 **Recent Bird Sightings**: Browse the latest bird observations from eBird's real-time database
- 🏆 **Rarity Scoring**: Discover rare and unusual species based on historical frequency analysis
- 🌍 **Regional Coverage**: Explore observations from countries, states, counties, and local birding hotspots
- � **Flexible Time Filters**: View observations from today, this week, or customize your timeframe
- 🔍 **Smart Search**: Find specific species or browse by rarity level
- 📱 **Mobile-Friendly**: Perfect for use in the field on any device
- � **Frequency Analysis**: Statistical smoothing provides accurate rarity assessments

## What Makes This Special

- 🧠 **Smart Rarity Assessment**: Uses statistical analysis of eBird frequency data to identify truly rare observations
- 🕒 **Real-time Data**: Shows the most recent bird observations from eBird's live database
- 🎯 **Regional Focus**: Tailored for specific birding regions, from countries to local hotspots
- 📊 **Data-Driven Insights**: Combines observation data with historical frequency patterns
- 🔍 **Birder-Friendly Interface**: Designed specifically for birders who want to find notable sightings

## Tech Stack

- **Data Source**: eBird API and frequency analysis
- **Frontend**: Modern web interface (Vue 3 + Vite)
- **Styling**: Clean, responsive design (Bulma CSS + custom styling)
- **Data Processing**: Python tools for frequency data management

## Quick Start

### Prerequisites

- Node.js 20.19.0+ or 22.12.0+
- Python 3.8+ (for data download scripts)
- uv (recommended) or pip for Python package management
- eBird account (for downloading bar chart data)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/rafnuss/eBirdRecentObservation.git
   cd eBirdRecentObservation
   ```

2. **Install Node.js dependencies**

   ```bash
   npm install
   ```

3. **Install Python dependencies** (optional, for data management)

   **Using uv (recommended - fast and modern):**

   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

   **Using traditional pip:**

   ```bash
   pip install -r requirements.txt
   ```

### Development

```bash
npm run dev
```

This starts the development server at `http://localhost:5173`

### Production Build

```bash
npm run build
```

### Quick Python Setup

If you have npm installed, you can use these convenient commands:

```bash
# Set up Python dependencies (using uv)
npm run setup:python

# Or using traditional pip
npm run setup:python-pip

# Download data for European countries
npm run download:europe

# Create/update manifest
npm run manifest:create
```

### Python Virtual Environment (Recommended)

For better dependency isolation, use uv to create a virtual environment:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Now you can run the script directly
python scripts/download_barchart.py CH FR DE
```

## Data Management

### Bar Chart Data Download

The application uses eBird bar chart data to calculate bird frequency and rarity scores. This data needs to be downloaded separately using the included Python script.

#### Prerequisites for Data Download

1. **eBird Account**: You need valid eBird credentials
2. **Environment Setup**: Create a `.env` file with your credentials

#### Setting Up Environment Variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your eBird credentials:

   ```bash
   EBIRD_USERNAME=your_ebird_username_here
   EBIRD_PASSWORD=your_ebird_password_here
   EBIRD_API_KEY=your_ebird_api_key_here
   ```

   > **Note**: The `EBIRD_API_KEY` is needed for fetching region information when creating the manifest.

#### Download Bar Chart Data

The `download_barchart.py` script supports both single and multiple region downloads:

**Single Region Downloads:**

```bash
# Download data for a specific region (e.g., Switzerland)
python scripts/download_barchart.py CH

# Download data for a French region (Grand Est)
python scripts/download_barchart.py FR-GES

# Force re-download even if file exists
python scripts/download_barchart.py CH --force

```

**Multiple Region Downloads:**

```bash
# Download data for multiple European countries
python scripts/download_barchart.py CH FR DE IT ES

# Download with custom delay between requests (respectful to eBird servers)
python scripts/download_barchart.py CH FR DE --delay 2.0

# Download from a file containing region codes
python scripts/download_barchart.py --from-file example_regions.txt

# Force re-download all regions, even if files exist
python scripts/download_barchart.py CH FR DE --force

# Download with minimal delay for faster processing
python scripts/download_barchart.py CH FR DE --delay 0.5
```

#### Create/Update Region Manifest

After downloading bar chart data, create a manifest file that maps region codes to human-readable names:

```bash
# Create manifest for all downloaded regions
python scripts/download_barchart.py --create-manifest
```

#### Understanding the Data

The downloaded JSON files contain:

- **Species List**: All bird species for the region
- **Frequency Data**: Weekly frequency values (48 weeks per year)
- **Sample Sizes**: Number of checklists per week
- **Taxonomic Information**: Scientific names, eBird codes, categories

## Project Structure

```txt
├── public/
│   ├── barchartData/          # Downloaded eBird bar chart data
│   │   ├── manifest.json      # Region code to name mapping
│   │   ├── CH.json           # Switzerland data
│   │   ├── FR.json           # France data
│   │   └── ...               # Other region files
│   └── assets/               # Static assets
├── src/
│   ├── components/           # Vue components
│   │   ├── ObservationList.vue
│   │   └── RegionSearch.vue
│   ├── config/              # Configuration files
│   │   └── api.js           # API endpoints and keys
│   ├── styles/              # Custom CSS
│   ├── utils/               # Utility functions
│   │   ├── manifest.js      # Region data utilities
│   │   └── smoothing.js     # Frequency smoothing algorithms
│   └── App.vue             # Main application component
├── scripts/
│   └── download_barchart.py  # Data download script
└── requirements.txt          # Python dependencies
```

## Configuration

### API Configuration

The application is configured via `src/config/api.js`:

- **eBird API Key**: Currently uses a demo key (replace for production)
- **Base URLs**: eBird API and data file paths
- **Endpoints**: Pre-configured API endpoint templates

### Deployment Configuration

For GitHub Pages deployment, the app is configured with:

- Base path: `/eBirdRecentObservation/`
- Static asset handling for production builds

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Use Vue 3 Composition API
- Follow the existing code style and naming conventions
- Add JSDoc comments for new functions
- Test with multiple regions before submitting
- Update documentation for new features

## Troubleshooting

### Common Issues

1. **No observations showing**: Check if bar chart data exists for your region
2. **Python script errors**: Verify eBird credentials in `.env` file
3. **Build errors**: Ensure Node.js version meets requirements
4. **API errors**: Check if eBird API is accessible and key is valid

### Data Issues

- **Missing regions**: Add new regions by running the download script
- **Outdated data**: Re-download with `--force` flag
- **Manifest errors**: Recreate with `--create-manifest`

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **eBird**: For providing the comprehensive bird observation data
- **Cornell Lab of Ornithology**: For maintaining the eBird platform
- **e2L Library**: For eBird data scraping capabilities
