<template>
  <div id="app">
    <!-- Dynamic Hero Section -->
    <section class="hero is-primary" :class="region ? 'hero-collapsed' : 'hero-fullscreen'">
      <div class="hero-body">
        <div class="container">
          <!-- Main Title (always visible) -->
          <div class="hero-content">
            <h1 class="title has-text-centered" :class="region ? 'is-3' : 'is-1'">
              eBird Recent Observations
            </h1>
            <h2 v-if="!region" class="subtitle is-4 has-text-centered mb-6">
              Discover recent bird observations in your region
            </h2>

            <!-- Region Search (always in hero) -->
            <div class="search-container">
              <div class="box search-box">
                <RegionSearch @region-selected="setRegion" :initial-region="region" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="section content-section" :class="{ 'content-visible': region }">
      <div class="container my-3">
        <!-- Observations List -->
        <ObservationList
          v-if="observations.length"
          :observations="observations"
          :regionCode="region.code"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import RegionSearch from "./components/RegionSearch.vue";
import ObservationList from "./components/ObservationList.vue";
import { getRegionFromManifest } from "./utils/manifest.js";
import { smoothFrequency } from "./utils/smoothing.js";
import { getEBirdApiUrl, getDataFileUrl, EBIRD_CONFIG } from "./config/api.js";

/**
 * Main application component for eBird Recent Observations
 * Manages region selection and displays recent bird observations with rarity scoring
 */

// Reactive state
const region = ref(null);
const observations = ref([]);
const barchart = ref({});
const isLoading = ref(false);

/**
 * Initialize the application by checking URL parameters for region selection
 */
onMounted(async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const regionCode = urlParams.get("region");

  if (regionCode) {
    await setRegionByCode(regionCode);
  }
});

/**
 * Set the selected region using a region code
 * @param {string} regionCode - eBird region code (e.g., 'CH', 'FR-GES')
 */
const setRegionByCode = async (regionCode) => {
  const regionData = await getRegionFromManifest(regionCode);

  if (regionData) {
    await setRegion(regionData);
  } else {
    updateURL(null);
  }
};

/**
 * Set the selected region and fetch associated data
 * @param {Object} regionData - Region object containing code, name, and type
 */
const setRegion = async (regionData) => {
  region.value = regionData;
  updateURL(regionData ? regionData.code : null);

  if (regionData) {
    await fetchData();
  }
};

const fetchData = async () => {
  if (!region.value) return;

  isLoading.value = true;
  const regionCode = region.value.code;

  try {
    // Fetch the barchart data for frequency calculations
    const barRes = await fetch(getDataFileUrl(`${regionCode}.json`));
    const barchartData = await barRes.json();

    // Extract sample sizes for frequency smoothing
    const sampleSizes = barchartData[1].samples_size.week;

    // Create lookup with species data for frequency calculations
    barchart.value = Object.fromEntries(
      barchartData[0].map((species, index) => [
        species.speciesCode,
        { ...species, order: index }, // Store taxonomic order and frequency data
      ])
    );

    // Fetch recent observations from eBird API
    const obsRes = await fetch(
      getEBirdApiUrl(EBIRD_CONFIG.ENDPOINTS.RECENT_OBSERVATIONS(regionCode))
    );
    const rawObservations = await obsRes.json();

    // Merge observations with frequency data for rarity scoring
    observations.value = rawObservations.map((obs) => {
      const speciesData = barchart.value[obs.speciesCode];

      // Calculate smoothed frequency using the observation date
      const frequency = speciesData?.freq
        ? smoothFrequency(speciesData.freq, sampleSizes, obs.obsDt)
        : speciesData?.frequency || null;

      const category = speciesData?.category || null;
      const order = speciesData?.order || null;
      return { ...obs, frequency, category, order };
    });
  } catch (error) {
    console.error("Error fetching data:", error);
  } finally {
    isLoading.value = false;
  }
};

/**
 * Update the browser URL to reflect the selected region
 * @param {string|null} regionCode - Region code to add to URL, or null to remove
 */
const updateURL = (regionCode) => {
  const url = new URL(window.location);

  if (regionCode) {
    url.searchParams.set("region", regionCode);
  } else {
    url.searchParams.delete("region");
  }

  // Update URL without reloading the page
  window.history.replaceState({}, "", url);
};
</script>

<style scoped>
@import "./styles/App.css";
</style>
