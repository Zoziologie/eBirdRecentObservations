/**
 * Frequency smoothing utility based on binomial variance weighting
 */

/**
 * Smooth frequency data using binomial variance-based weighting
 *
 * @param {number[]} frequencies - Array of frequency values (0-1) for 48 weeks
 * @param {number[]} sampleSizes - Array of sample sizes for each week
 * @param {string} observationDate - ISO date string of the observation (e.g., "2025-10-04")
 * @param {number} targetObs - Target number of observations for smoothing
 * @returns {number} Smoothed frequency value
 */
export function smoothFrequency(frequencies, sampleSizes, observationDate, targetObs = 10) {
  const targetWeek = getWeekFromDate(observationDate);
  const maxWeeks = frequencies.length;

  // Find the window of weeks around target week
  let start = targetWeek;
  let end = targetWeek;
  let currentFreq, currentSamples, requiredSamples;

  // Expand window until we reach required samples
  while (true) {
    // Calculate current frequency estimate with current window
    [currentFreq, currentSamples] = calculateWeightedAverage(frequencies, sampleSizes, start, end);

    // Calculate required sample size based on current frequency estimate
    if (currentFreq === 0) {
      requiredSamples = 1000; // Use large sample size when no observations
    } else {
      requiredSamples = targetObs / currentFreq;
    }

    // Check if we have enough samples
    if (currentSamples >= requiredSamples) {
      break;
    }

    // Expand in both directions if possible
    const canExpandLeft = start > 0;
    const canExpandRight = end < maxWeeks - 1;

    if (!canExpandLeft && !canExpandRight) {
      break; // Can't expand anymore
    }

    if (canExpandLeft) start--;
    if (canExpandRight) end++;
  }

  // Return the final frequency estimate
  return currentFreq;
}

/**
 * Calculate weighted average frequency for a given week range
 * @param {number[]} frequencies - Array of frequency values (0-1) for 47 weeks
 * @param {number[]} sampleSizes - Array of sample sizes for each week
 * @param {number} start - Start week index
 * @param {number} end - End week index
 * @returns {[number, number]} [weightedAverage, totalSamples]
 */
function calculateWeightedAverage(frequencies, sampleSizes, start, end) {
  const freqSlice = frequencies.slice(start, end + 1);
  const sampleSlice = sampleSizes.slice(start, end + 1);

  const weightedSum = freqSlice.reduce((sum, freq, i) => {
    const samples = sampleSlice[i] || 0;
    return sum + (freq || 0) * samples;
  }, 0);

  const totalSamples = sampleSlice.reduce((sum, samples) => sum + (samples || 0), 0);

  const weightedAverage = totalSamples > 0 ? weightedSum / totalSamples : 0;
  return [weightedAverage, totalSamples];
}

/**
 * Legacy frequency smoothing function using statistical confidence intervals
 * @deprecated Use smoothFrequency() instead
 *
 * @param {number[]} frequencies - Array of frequency values (0-1) for 47 weeks
 * @param {number[]} sampleSizes - Array of sample sizes for each week
 * @param {number} targetAccuracy - Target margin of error E (default: 0.2 = 20%)
 * @param {number} confidenceLevel - Confidence level (default: 0.8 = 80%)
 * @returns {number} Smoothed frequency value
 */
export function smoothFrequencyOld(
  frequencies,
  sampleSizes,
  targetAccuracy = 0.2,
  confidenceLevel = 0.8
) {
  const currentWeek = getCurrentWeek();
  const maxWeeks = frequencies.length;

  // Calculate z-score for confidence level
  const alpha = 1 - confidenceLevel;
  const zScore = getZScore(1 - alpha / 2); // z_{1-α/2}

  // Find the window of weeks around current week
  let start = currentWeek;
  let end = currentWeek;
  let currentFreq, currentSamples, requiredSamples;

  // Expand window until we reach required samples
  while (true) {
    // Calculate current frequency estimate with current window
    [currentFreq, currentSamples] = calculateWeightedAverage(frequencies, sampleSizes, start, end);

    // Calculate required sample size based on current frequency estimate: n = z²p(1-p)/E²
    if (currentFreq === 0) {
      requiredSamples = 1000; // Use large sample size when no observations
    } else {
      const E = targetAccuracy * currentFreq; // Adjust E based on current frequency
      requiredSamples = Math.ceil((zScore * zScore * currentFreq * (1 - currentFreq)) / (E * E));
    }

    // Check if we have enough samples
    if (currentSamples >= requiredSamples) {
      break;
    }

    // Expand in both directions if possible
    const canExpandLeft = start > 0;
    const canExpandRight = end < maxWeeks - 1;

    if (!canExpandLeft && !canExpandRight) {
      break; // Can't expand anymore
    }

    if (canExpandLeft) start--;
    if (canExpandRight) end++;
  }

  // Return the final frequency estimate
  return currentFreq;
}

/**
 * Get z-score for given probability (approximate)
 * @param {number} p - Probability (e.g., 0.975 for 95% confidence)
 * @returns {number} Z-score
 */
function getZScore(p) {
  // Common z-scores for confidence intervals
  const zTable = {
    0.9: 1.282, // 80% CI
    0.95: 1.645, // 90% CI
    0.975: 1.96, // 95% CI
    0.99: 2.326, // 98% CI
    0.995: 2.576, // 99% CI
  };

  return zTable[p] || 1.96; // Default to 95% CI
}

/**
 * Get the current week of the year (0-47 for eBird data)
 * eBird uses 48 time periods across the year (approximately 7.6 days each)
 *
 * @returns {number} Current week (0-based index, 0-47)
 */
export function getCurrentWeek() {
  const now = new Date();
  return getWeekFromDate(now.toISOString().split("T")[0]);
}

/**
 * Get the week number from a specific date (0-47 for eBird data)
 * eBird uses 48 time periods across the year (approximately 7.6 days each)
 *
 * @param {string} dateString - ISO date string (e.g., "2025-10-04")
 * @returns {number} Week number (0-based index, 0-47)
 */
export function getWeekFromDate(dateString) {
  const targetDate = new Date(dateString);
  const start = new Date(targetDate.getFullYear(), 0, 1);
  const dayOfYear = Math.floor((targetDate - start) / 86400000) + 1;

  // eBird divides the year into 48 periods
  // Each period is approximately 365.25/48 ≈ 7.6 days
  const periodLength = 365.25 / 48;
  const weekNumber = Math.min(47, Math.floor((dayOfYear - 1) / periodLength));

  return weekNumber; // Return 0-based index (0-47)
}
