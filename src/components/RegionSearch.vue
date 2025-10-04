<template>
  <div class="region-search-container">
    <multiselect
      v-model="selectedRegion"
      :options="regions"
      :searchable="true"
      :loading="loading"
      :clear-on-select="true"
      :close-on-select="true"
      :internal-search="false"
      :allow-empty="false"
      label="name"
      track-by="code"
      placeholder="Search among available regions..."
      select-label=""
      selected-label=""
      deselect-label=""
      @search-change="onSearch"
      @select="onSelect"
    >
      <template #option="{ option }">
        <span>{{ option.name }} ({{ option.code }})</span>
      </template>
      <template #singleLabel="{ option }">
        <span>{{ option.name }} ({{ option.code }})</span>
      </template>
      <template #noResult>
        <div class="no-result-message">
          <div class="no-result-content">
            <p class="no-result-text">Region not found in our database.</p>
            <p class="no-result-suggestion">
              <strong>Want to add this region?</strong>
            </p>
            <a
              :href="getNewRegionIssueUrl()"
              target="_blank"
              rel="noopener noreferrer"
              class="button is-small is-primary"
            >
              <span class="icon">
                <i class="fab fa-github"></i>
              </span>
              <span>Request Region</span>
            </a>
          </div>
        </div>
      </template>
    </multiselect>

    <a
      v-if="selectedRegion"
      :href="`https://ebird.org/region/${selectedRegion.code}`"
      target="_blank"
      rel="noopener noreferrer"
      class="ebird-link"
      title="View this region on eBird"
    >
      <img src="/ebird_logo_letter.svg" alt="eBird" class="ebird-favicon" />
    </a>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import Multiselect from "vue-multiselect";
import "vue-multiselect/dist/vue-multiselect.min.css";
import { loadManifest } from "../utils/manifest.js";
import { APP_CONFIG } from "../config/api.js";

/**
 * RegionSearch Component
 * Provides a searchable dropdown for selecting eBird regions
 * Includes functionality to request new regions via GitHub issues
 */

// Define props
const props = defineProps({
  initialRegion: { type: Object, default: null },
});

// Define emits
const emit = defineEmits(["region-selected"]);

// Reactive state
const regions = ref([]);
const manifestRegions = ref([]);
const selectedRegion = ref(null);
const currentSearchTerm = ref("");

/**
 * Watch for changes to initialRegion prop and update selected region
 */
watch(
  () => props.initialRegion,
  (newRegion) => {
    if (newRegion) {
      selectedRegion.value = newRegion;
    } else {
      selectedRegion.value = null;
    }
  },
  { immediate: true }
);

/**
 * Initialize component by loading available regions from manifest
 */
onMounted(async () => {
  manifestRegions.value = await loadManifest();
  // Initialize regions with manifest data so users can see available options
  regions.value = manifestRegions.value;
});

/**
 * Handle search input changes and filter available regions
 * @param {string} search - Search term entered by user
 */
const onSearch = (search) => {
  currentSearchTerm.value = search; // Store the current search term

  // If search is empty or very short, show all manifest regions
  if (!search || search.length < 2) {
    regions.value = manifestRegions.value;
    return;
  }

  // Filter from manifest regions only
  const manifestResults = manifestRegions.value.filter(
    (region) =>
      region.name.toLowerCase().includes(search.toLowerCase()) ||
      region.code.toLowerCase().includes(search.toLowerCase())
  );

  regions.value = manifestResults;
};

/**
 * Handle region selection and emit event to parent component
 * @param {Object} region - Selected region object with code, name, and type
 */
const onSelect = (region) => {
  emit("region-selected", region);
};

/**
 * Generate GitHub issue URL for requesting a new region
 * @returns {string} Complete GitHub issue URL with pre-filled content
 */
const getNewRegionIssueUrl = () => {
  const baseUrl = `${APP_CONFIG.GITHUB_REPO_URL}/issues/new`;
  const title = `Add new region: ${currentSearchTerm.value || "Region name"}`;
  const body = `## New Region Request

**Region Name:** ${currentSearchTerm.value || "Please specify the region name"}

**eBird Region Code:** (if known)

**Additional Information:**
- Please provide the official eBird region code for this area
- Include any relevant geographic details
- Mention if this is a country, state, county, or specific birding location

**Why is this region needed?**
(Describe why you'd like to see recent observations for this region)

---
*This issue was automatically created from the region search interface.*`;

  const params = new URLSearchParams({
    title,
    body,
    labels: "enhancement,region-request",
  });

  return `${baseUrl}?${params.toString()}`;
};
</script>

<style scoped>
/* Region search container with eBird link */
.region-search-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.multiselect {
  flex: 1;
}

.ebird-link {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(159, 174, 68, 0.3);
  transition: all 0.2s ease;
  text-decoration: none;
}

.ebird-link:hover {
  background: rgba(159, 174, 68, 0.1);
  border-color: #9fae44;
  transform: translateY(-1px);
}

.ebird-favicon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

/* Simple background color styling to match the design */
:deep(.multiselect__option--highlight) {
  background: rgba(159, 174, 68, 0.2);
  color: #3a3a3a;
}

:deep(.multiselect__option--selected) {
  background: #9fae44;
  color: white;
}

/* Fix z-index to appear above other elements */
:deep(.multiselect__content-wrapper) {
  z-index: 99999;
  position: absolute;
}

:deep(.multiselect) {
  position: relative;
  z-index: 99998;
}

/* No result message styling */
.no-result-message {
  padding: 1rem;
  text-align: center;
  border-top: 1px solid rgba(159, 174, 68, 0.2);
}

.no-result-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: center;
}

.no-result-text {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.no-result-suggestion {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.no-result-message .button {
  border-radius: 8px;
  font-size: 0.8rem;
  background: linear-gradient(135deg, var(--apple-green), var(--dark-moss-green));
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.no-result-message .button:hover {
  background: linear-gradient(135deg, var(--citron-2), var(--apple-green));
  transform: translateY(-1px);
}
</style>
