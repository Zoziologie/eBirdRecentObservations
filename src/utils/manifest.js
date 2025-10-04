/**
 * Utility functions for loading and transforming eBird region manifest data
 * The manifest contains mappings from region codes to region names and types
 */

import { getDataFileUrl } from "../config/api.js";

/**
 * Load and transform the complete region manifest from the server
 * @returns {Promise<Object[]>} Array of region objects with code, name, and type properties
 */
export const loadManifest = async () => {
  try {
    const response = await fetch(getDataFileUrl("manifest.json"));
    const manifest = await response.json();

    // Transform manifest data to match the expected format
    return Object.entries(manifest).map(([code, data]) => ({
      code: code,
      name: data.result || code, // Use result as name, fallback to code
      type: data.type || "region",
    }));
  } catch (error) {
    console.error("Error loading manifest:", error);
    return [];
  }
};

/**
 * Get specific region data from manifest by region code
 * @param {string} regionCode - eBird region code (e.g., 'CH', 'FR-GES')
 * @returns {Promise<Object|null>} Region object or null if not found
 */
export const getRegionFromManifest = async (regionCode) => {
  try {
    const response = await fetch(getDataFileUrl("manifest.json"));
    const manifest = await response.json();

    if (manifest[regionCode]) {
      return {
        code: regionCode,
        name: manifest[regionCode].result || regionCode,
        type: manifest[regionCode].type || "region",
      };
    }
    return null;
  } catch (error) {
    console.error("Error getting region from manifest:", error);
    return null;
  }
};
