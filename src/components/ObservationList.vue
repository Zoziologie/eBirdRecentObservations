<template>
  <div class="box">
    <!-- Header -->
    <div class="level">
      <div class="level-left">
        <div class="level-item">
          <div>
            <h3 class="title is-4">Recent Observations</h3>
            <p class="subtitle is-6">
              {{ filteredObservations.length }} species (of {{ observations.length }} total)
            </p>
          </div>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <div class="field has-addons mr-3">
            <div class="control">
              <input
                v-model.number="daysSince"
                type="number"
                class="input"
                placeholder="Days"
                min="1"
                max="30"
                style="width: 80px"
              />
            </div>
            <div class="control">
              <span class="button is-static">days</span>
            </div>
          </div>
        </div>
        <div class="level-item">
          <div class="field has-addons mr-3">
            <div class="control">
              <span class="button is-static">Sort by</span>
            </div>
            <div class="control">
              <div class="select">
                <select v-model="sortBy">
                  <option value="rarity">Rarity</option>
                  <option value="taxonomy">Taxonomy</option>
                  <option value="date">Last Observed</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="level-item">
          <div class="field has-addons">
            <div class="control">
              <input v-model="searchTerm" class="input" placeholder="Search species..." />
            </div>
            <div class="control">
              <button class="button is-info" @click="searchTerm = ''">
                <span class="icon">
                  <i class="fas fa-times"></i>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compact Species List -->
    <div class="species-list">
      <div v-for="obs in filteredObservations" :key="obs.speciesCode" class="species-item">
        <!-- Species Row -->
        <div class="observation-row">
          <div class="rarity-column">
            <span
              class="tag is-small"
              :class="getRarityClass(obs.frequency ? Math.max(0, 1 - obs.frequency) : null)"
            >
              {{ obs.frequency ? (Math.max(0, 1 - obs.frequency) * 10).toFixed(1) : "N/A" }}
            </span>
          </div>

          <div class="species-column">
            <div class="species-info">
              <div class="names">
                <a
                  :href="getSpeciesUrl(obs.speciesCode)"
                  target="_blank"
                  class="common-name species-link"
                >
                  {{ obs.comName }}
                </a>
                <div class="scientific-name-container">
                  <span class="scientific-name">{{ obs.sciName }}</span>
                  <span
                    v-if="obs.category && obs.category !== 'species'"
                    class="category-icon"
                    :title="`Category: ${obs.category}`"
                  >
                    🔍
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="location-column">
            <span class="icon is-small">
              <i class="fas fa-map-marker-alt"></i>
            </span>
            <span class="location-name">{{ obs.locName }}</span>
          </div>

          <div class="date-column">
            <span class="icon is-small">
              <i class="fas fa-clock"></i>
            </span>
            <span class="date-text">{{ formatDate(obs.obsDt) }}</span>
          </div>

          <div class="actions-column">
            <div class="action-buttons">
              <a
                :href="getChecklistUrl(obs.subId)"
                target="_blank"
                class="button is-small is-link is-light"
                title="View eBird checklist"
              >
                <span class="icon">
                  <i class="fas fa-external-link-alt"></i>
                </span>
              </a>
              <button
                @click="toggleSightings(obs)"
                class="button is-small is-info"
                :class="{ 'is-loading': loadingSightings[obs.speciesCode] }"
                :disabled="loadingSightings[obs.speciesCode]"
              >
                <span class="icon">
                  <i
                    class="fas"
                    :class="allSightings[obs.speciesCode] ? 'fa-chevron-up' : 'fa-chevron-down'"
                  ></i>
                </span>
                <span>{{ allSightings[obs.speciesCode] ? "Hide" : "Show" }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- All Sightings (Collapsible) -->
        <div
          v-if="allSightings[obs.speciesCode]"
          class="sightings-list p-3 has-background-white-bis"
        >
          <h6 class="title is-6 mb-3 has-text-grey-dark">
            <span class="icon binoculars-icon">
              <i class="fas fa-binoculars"></i>
            </span>
            All Recent Sightings ({{ allSightings[obs.speciesCode].length }})
          </h6>

          <!-- Compact Sightings Grid -->
          <div class="sightings-grid">
            <div
              v-for="sighting in allSightings[obs.speciesCode]"
              :key="sighting.obsId"
              class="sighting-card"
            >
              <div class="box is-small p-3">
                <div class="sighting-content">
                  <!-- Count -->
                  <div class="sighting-item">
                    <span class="icon is-small">
                      <i class="fas fa-hashtag"></i>
                    </span>
                    <span class="sighting-text">
                      {{ sighting.howMany || "X" }} individual{{
                        sighting.howMany && sighting.howMany > 1 ? "s" : ""
                      }}
                    </span>
                  </div>

                  <!-- Date & Time -->
                  <div class="sighting-item">
                    <span class="icon is-small">
                      <i class="fas fa-clock"></i>
                    </span>
                    <span class="sighting-text">
                      {{ formatDateLocal(sighting.obsDt) }} at {{ formatTime(sighting.obsDt) }}
                    </span>
                  </div>

                  <!-- Location -->
                  <div class="sighting-item">
                    <span class="icon is-small">
                      <i class="fas fa-map-marker-alt"></i>
                    </span>
                    <span class="sighting-text">{{ sighting.locName }}</span>
                  </div>

                  <!-- Checklist Link -->
                  <div class="sighting-actions">
                    <a
                      :href="getChecklistUrl(sighting.subId)"
                      target="_blank"
                      class="button is-small is-link is-light"
                      title="View eBird checklist"
                    >
                      <span class="icon is-small">
                        <i class="fas fa-external-link-alt"></i>
                      </span>
                      <span>Checklist</span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results Message -->
    <div v-if="!filteredObservations.length && searchTerm" class="notification is-warning is-light">
      <span class="icon">
        <i class="fas fa-exclamation-triangle"></i>
      </span>
      No observations found matching "{{ searchTerm }}".
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { getEBirdApiUrl, EBIRD_CONFIG, APP_CONFIG } from "../config/api.js";

/**
 * ObservationList Component
 * Displays and manages a list of recent bird observations with filtering and sorting capabilities
 */

// Props
const props = defineProps({
  observations: { type: Array, required: true },
  regionCode: { type: String, required: true }, // Need region code for API calls
});

// Reactive state
const searchTerm = ref("");
const daysSince = ref(5); // Default to 5 days
const sortBy = ref("rarity"); // Default sort by rarity
const allSightings = ref({}); // Store all sightings for each species
const loadingSightings = ref({}); // Track loading state for each species

/**
 * Computed property to filter and sort observations based on user criteria
 * @returns {Object[]} Filtered and sorted array of observations
 */
const filteredObservations = computed(() => {
  let filtered = props.observations;

  // Filter by days since observation
  if (daysSince.value) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysSince.value);

    filtered = filtered.filter((obs) => {
      const obsDate = new Date(obs.obsDt);
      return obsDate >= cutoffDate;
    });
  }

  // Filter by search term
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(
      (obs) => obs.comName.toLowerCase().includes(term) || obs.sciName.toLowerCase().includes(term)
    );
  }

  // Sort the results
  return sortObservations(filtered);
});

/**
 * Sort observations based on the selected sorting criteria
 * @param {Object[]} observations - Array of observation objects to sort
 * @returns {Object[]} Sorted array of observations
 */
const sortObservations = (observations) => {
  const sorted = [...observations]; // Create a copy to avoid mutating original

  switch (sortBy.value) {
    case "rarity":
      return sorted.sort((a, b) => {
        // Sort by rarity score (highest/rarest first)
        const rarityA = a.frequency ? Math.max(0, 1 - a.frequency) : null;
        const rarityB = b.frequency ? Math.max(0, 1 - b.frequency) : null;

        if (rarityA === null && rarityB === null) return 0;
        if (rarityA === null) return 1;
        if (rarityB === null) return -1;
        return rarityB - rarityA;
      });

    case "taxonomy":
      return sorted.sort((a, b) => {
        // Sort by taxonomic order from observation data
        const orderA = a.order;
        const orderB = b.order;

        // If order not available, put them at the end
        if (orderA === null && orderB === null) return 0;
        if (orderA === null) return 1;
        if (orderB === null) return -1;

        return orderA - orderB;
      });

    case "date":
      return sorted.sort((a, b) => {
        // Sort by observation date (most recent first)
        const dateA = new Date(a.obsDt);
        const dateB = new Date(b.obsDt);
        return dateB - dateA;
      });

    default:
      return sorted;
  }
};

/**
 * Toggle visibility of all sightings for a species
 * @param {Object} obs - Observation object containing species information
 */
const toggleSightings = async (obs) => {
  const speciesCode = obs.speciesCode;

  // If already loaded, just toggle visibility
  if (allSightings.value[speciesCode]) {
    // Remove to hide
    delete allSightings.value[speciesCode];
    return;
  }

  // Load sightings
  await loadAllSightings(obs);
};

/**
 * Load all recent sightings for a specific species from eBird API
 * @param {Object} obs - Observation object containing species information
 */
const loadAllSightings = async (obs) => {
  const speciesCode = obs.speciesCode;

  // Check if regionCode is available
  if (!props.regionCode) {
    alert("Region code is not available. Please select a region first.");
    return;
  }

  // Set loading state
  loadingSightings.value[speciesCode] = true;
  const apiUrl = getEBirdApiUrl(
    EBIRD_CONFIG.ENDPOINTS.RECENT_SPECIES(props.regionCode, speciesCode)
  );

  try {
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`Failed to fetch sightings for ${obs.comName} (${response.status})`);
    }

    const sightings = await response.json();
    allSightings.value[speciesCode] = sightings;
  } catch (error) {
    console.error(`Error loading sightings for ${obs.comName}:`, error);
    alert(`Could not load all sightings for ${obs.comName}`);
  } finally {
    loadingSightings.value[speciesCode] = false;
  }
};

/**
 * Format observation date for display with relative time
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
const formatDate = (dateString) => {
  const date = new Date(dateString);
  const today = new Date();
  const diffTime = today - date;
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return "Today";
  } else if (diffDays === 1) {
    return "Yesterday";
  } else if (diffDays <= 5) {
    return `${diffDays} days ago`;
  } else {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }
};

/**
 * Format observation date for local display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string using local settings
 */
const formatDateLocal = (dateString) => {
  const date = new Date(dateString);
  const today = new Date();
  const diffTime = today - date;
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return "Today";
  } else if (diffDays === 1) {
    return "Yesterday";
  } else if (diffDays <= 5) {
    return `${diffDays} days ago`;
  } else {
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }
};

/**
 * Format time from date string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted time string (HH:MM)
 */
const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

/**
 * Generate eBird checklist URL
 * @param {string} subId - eBird submission ID
 * @returns {string} Complete URL to eBird checklist
 */
const getChecklistUrl = (subId) => {
  return `${APP_CONFIG.EBIRD_BASE_URL}/checklist/${subId}`;
};

/**
 * Generate eBird species page URL for the current region
 * @param {string} speciesCode - eBird species code
 * @returns {string} Complete URL to eBird species page
 */
const getSpeciesUrl = (speciesCode) => {
  return `${APP_CONFIG.EBIRD_BASE_URL}/species/${speciesCode}/${props.regionCode}`;
};

/**
 * Get CSS class for rarity badge based on rarity score
 * @param {number|null} rarityScore - Rarity score (0-1, where 1 is rarest)
 * @returns {string} CSS class name for styling the rarity badge
 */
const getRarityClass = (rarityScore) => {
  if (rarityScore === null || rarityScore === undefined) {
    return "is-light"; // Unknown rarity
  }
  const rarity = parseFloat(rarityScore);

  // Adjusted thresholds for better visibility:
  if (rarity >= 0.9855) return "is-danger"; // Extremely rare (< 10% frequency)
  if (rarity >= 0.94555) return "is-warning"; // Very rare (10-25% frequency)
  if (rarity >= 0.8955) return "is-info"; // Uncommon (25-50% frequency)
  return "is-success"; // Common (> 50% frequency)
};
</script>

<style>
@import "../styles/App.css";
</style>

<style scoped>
/* Compact Table Layout */
.observation-header {
  border-bottom: 2px solid rgba(159, 174, 68, 0.2);
  margin-bottom: 0.5rem;
}

.header-row {
  display: grid;
  grid-template-columns: auto 1fr auto auto auto;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: rgba(159, 174, 68, 0.05);
  font-size: 0.875rem;
  align-items: center;
}

.observation-row {
  display: grid;
  grid-template-columns: auto 1fr auto auto auto;
  gap: 1rem;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid rgba(159, 174, 68, 0.1);
  transition: background-color 0.2s ease;
  align-items: center;
}

/* Ensure all columns have consistent alignment */
.header-row > div,
.observation-row > div {
  display: flex;
  align-items: center;
}

.rarity-column,
.actions-column {
  justify-content: center;
}

.species-column,
.location-column,
.date-column {
  justify-content: flex-start;
}

.location-column,
.date-column {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Ensure header and row icons align */
.header-row .location-column,
.header-row .date-column,
.observation-row .location-column,
.observation-row .date-column {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.observation-row:hover {
  background: rgba(159, 174, 68, 0.03);
}

.species-column {
  min-width: 0; /* Allow text truncation */
}

.species-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.names {
  display: flex;
  align-items: baseline;
  min-width: 0;
  gap: 0.75rem;
}

.common-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.species-link {
  text-decoration: none;
  color: inherit;
  transition: color 0.2s ease;
}

.species-link:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.scientific-name {
  font-style: italic;
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.scientific-name-container {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}

.category-icon {
  font-size: 0.7rem;
  opacity: 0.7;
  flex-shrink: 0;
  cursor: help;
}

.species-column {
  min-width: 0; /* Allow text truncation */
}

.location-column,
.rarity-column,
.date-column,
.actions-column {
  flex-shrink: 0;
  text-align: center;
}

.location-name {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.species-item {
  margin-bottom: 0;
}

/* Responsive adjustments */
@media screen and (max-width: 768px) {
  .header-row,
  .observation-row {
    grid-template-columns: auto 1fr auto;
    gap: 0.5rem;
  }

  .location-column,
  .date-column {
    display: none;
  }

  .actions-column {
    justify-self: end;
  }

  .species-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

/* Main container */
.box {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(159, 174, 68, 0.15);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(102, 105, 47, 0.08), 0 4px 16px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
}

/* Header styling */
.title {
  color: var(--dark-moss-green);
  font-weight: 700;
}

.subtitle {
  color: var(--text-secondary);
  font-weight: 500;
}

/* Search input */
.input {
  border: 2px solid rgba(159, 174, 68, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.input:focus {
  border-color: var(--apple-green);
  box-shadow: 0 0 0 0.125em rgba(159, 174, 68, 0.25);
}

.input::placeholder {
  color: var(--text-muted);
}

/* Search clear button */
.field .button.is-info {
  background: linear-gradient(135deg, var(--citron-2), var(--citron));
  border: none;
  color: var(--walnut-brown);
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.field .button.is-info:hover {
  background: linear-gradient(135deg, var(--apple-green), var(--citron-2));
  transform: translateY(-1px);
}

/* Species header */
.species-header {
  background: linear-gradient(135deg, var(--light-citron) 0%, var(--light-apple) 100%) !important;
  border-radius: 16px;
  border: 1px solid rgba(205, 206, 113, 0.2);
  transition: all 0.3s ease;
}

.species-header:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 105, 47, 0.12);
  background: linear-gradient(
    135deg,
    rgba(205, 206, 113, 0.15) 0%,
    rgba(159, 174, 68, 0.12) 100%
  ) !important;
}

/* Species icon */
.species-header .icon {
  color: var(--apple-green) !important;
}

/* Species names */
.species-header .is-size-5 {
  color: var(--dark-moss-green);
  font-weight: 600;
}

.species-header .is-size-7 {
  color: var(--text-secondary);
  font-style: italic;
}

/* Tags styling */
.tag {
  border-radius: 6px;
  font-weight: 600;
  border: 1px solid transparent;
  min-width: 60px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
}

.tag.is-small {
  font-size: 0.75rem;
  min-width: 55px;
  height: 28px;
  padding: 0 6px;
}

/* Rarity tags with natural colors */
.tag.is-danger {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.tag.is-warning {
  background: linear-gradient(135deg, var(--citron-2), #f39c12);
  color: var(--walnut-brown);
}

.tag.is-info {
  background: linear-gradient(135deg, var(--apple-green), var(--citron));
  color: white;
}

.tag.is-success {
  background: linear-gradient(135deg, var(--dark-moss-green), var(--apple-green));
  color: white;
}

.tag.is-light {
  background: var(--light-walnut);
  color: var(--text-secondary);
  border-color: rgba(159, 174, 68, 0.2);
}

/* Button styling */
.button.is-small {
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.button.is-link {
  background: linear-gradient(135deg, var(--citron), var(--apple-green));
  border: none;
  color: white;
}

.button.is-link:hover {
  background: linear-gradient(135deg, var(--apple-green), var(--dark-moss-green));
  transform: translateY(-1px);
}

.button.is-link.is-light {
  background: rgba(159, 174, 68, 0.1);
  color: var(--dark-moss-green);
  border: 1px solid rgba(159, 174, 68, 0.3);
}

.button.is-link.is-light:hover {
  background: rgba(159, 174, 68, 0.2);
  border-color: var(--apple-green);
}

/* Toggle/Show button */
.actions-column .button.is-info {
  background: linear-gradient(135deg, var(--apple-green), var(--dark-moss-green));
  border: none;
  color: white;
  border-radius: 12px;
}

.actions-column .button.is-info:hover {
  background: linear-gradient(135deg, var(--citron-2), var(--apple-green));
}

/* Sightings section */
.sightings-list {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, var(--light-moss) 100%);
  border-radius: 0 0 16px 16px;
  border-top: 2px solid rgba(159, 174, 68, 0.2);
}

.sightings-list .title {
  color: var(--walnut-brown);
}

/* Fix binoculars icon rotation */
.binoculars-icon .fa-binoculars {
  transform: none !important;
  animation: none !important;
}

/* Sightings grid layout (replaces Bulma columns) */
.sightings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

/* Responsive adjustments for sightings grid */
@media screen and (max-width: 768px) {
  .sightings-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
}

@media screen and (min-width: 769px) and (max-width: 1023px) {
  .sightings-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

/* Individual sighting cards */
.sightings-list .box {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(205, 206, 113, 0.2);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(102, 105, 47, 0.08);
  transition: all 0.3s ease;
}

.sightings-list .box:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 105, 47, 0.12);
  border-color: var(--apple-green);
}

/* Sighting content layout */
.sighting-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sighting-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.sighting-item .icon {
  color: var(--apple-green);
  flex-shrink: 0;
}

.sighting-text {
  color: var(--text-secondary);
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sighting-actions {
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(159, 174, 68, 0.1);
}

.sighting-actions .button {
  width: 100%;
  justify-content: center;
}

.sightings-list .is-size-7 {
  color: var(--text-secondary);
}

.sightings-list .has-text-weight-semibold {
  color: var(--dark-moss-green);
}

.sightings-list .has-text-info {
  color: var(--apple-green) !important;
  font-weight: 600;
}

/* Loading state */
.button.is-loading {
  background: var(--light-walnut);
  color: var(--walnut-brown);
}

/* No results message */
.notification.is-warning {
  background: linear-gradient(135deg, rgba(205, 199, 74, 0.1) 0%, rgba(205, 206, 113, 0.1) 100%);
  border: 1px solid rgba(205, 199, 74, 0.3);
  color: var(--walnut-brown);
  border-radius: 16px;
}

/* Responsive design */
@media screen and (max-width: 768px) {
  .species-header {
    padding: 1rem !important;
  }

  .sightings-list {
    padding: 1rem !important;
  }

  .button.is-small {
    font-size: 0.7rem;
  }
}

/* Smooth animations */
.species-item {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.species-item:nth-child(1) {
  animation-delay: 0.1s;
}
.species-item:nth-child(2) {
  animation-delay: 0.2s;
}
.species-item:nth-child(3) {
  animation-delay: 0.3s;
}
.species-item:nth-child(4) {
  animation-delay: 0.4s;
}
.species-item:nth-child(5) {
  animation-delay: 0.5s;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
