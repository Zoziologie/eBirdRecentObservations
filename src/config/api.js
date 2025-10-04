/**
 * API Configuration
 * Contains API endpoints and keys for the eBird Recent Observations application
 */

/**
 * eBird API configuration
 * Note: This is a demo API key. For production use, store in environment variables.
 */
export const EBIRD_CONFIG = {
  // Demo API key - replace with environment variable for production
  API_KEY: "jfekjedvescr",
  BASE_URL: "https://api.ebird.org/v2",

  // API endpoints
  ENDPOINTS: {
    RECENT_OBSERVATIONS: (regionCode) =>
      `/data/obs/${regionCode}/recent?key=${EBIRD_CONFIG.API_KEY}&includeProvisional=true`,
    RECENT_SPECIES: (regionCode, speciesCode) =>
      `/data/obs/${regionCode}/recent/${speciesCode}?key=${EBIRD_CONFIG.API_KEY}`,
    REGION_INFO: (regionCode) => `/ref/region/info/${regionCode}`,
  },
};

/**
 * Application configuration
 */
export const APP_CONFIG = {
  // Base path for static data files
  DATA_BASE_PATH: "/eBirdRecentObservation/barchartData",

  // External URLs
  EBIRD_BASE_URL: "https://ebird.org",
  GITHUB_REPO_URL: "https://github.com/Zoziologie/eBirdRecentObservations",
};

/**
 * Get complete eBird API URL
 * @param {string} endpoint - API endpoint path
 * @returns {string} Complete API URL
 */
export function getEBirdApiUrl(endpoint) {
  return `${EBIRD_CONFIG.BASE_URL}${endpoint}`;
}

/**
 * Get complete data file URL
 * @param {string} filename - Data file name
 * @returns {string} Complete data file URL
 */
export function getDataFileUrl(filename) {
  return `${APP_CONFIG.DATA_BASE_PATH}/${filename}`;
}
