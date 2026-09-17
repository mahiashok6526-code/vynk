/**
 * Vynk Platform Currency Utilities
 * Primary currency: INR (₹)
 * Designed to be extensible for multi-currency support.
 */

export const CURRENCY_SYMBOLS = {
  INR: '₹',
  USD: '$',
  EUR: '€',
  GBP: '£',
};

/**
 * Format a numeric amount into a localized currency string.
 * Defaults to INR (₹) as the platform primary currency.
 *
 * @param {number|string} amount - The numeric monetary value
 * @param {string} currency - 3-letter currency code (default: 'INR')
 * @param {boolean} compact - Whether to use compact notation (e.g. 50K, 25L)
 * @returns {string} Formatted currency string with symbol
 */
export function formatCurrency(amount, currency = 'INR', compact = false) {
  const numericAmount = Number(amount) || 0;
  const symbol = CURRENCY_SYMBOLS[currency?.toUpperCase()] || '₹';

  if (compact) {
    if (currency === 'INR') {
      if (numericAmount >= 10000000) {
        return `${symbol}${(numericAmount / 10000000).toFixed(1).replace(/\.0$/, '')}Cr`;
      }
      if (numericAmount >= 100000) {
        return `${symbol}${(numericAmount / 100000).toFixed(1).replace(/\.0$/, '')}L`;
      }
      if (numericAmount >= 1000) {
        return `${symbol}${(numericAmount / 1000).toFixed(0)}K`;
      }
      return `${symbol}${numericAmount}`;
    } else {
      if (numericAmount >= 1000000) {
        return `${symbol}${(numericAmount / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
      }
      if (numericAmount >= 1000) {
        return `${symbol}${(numericAmount / 1000).toFixed(0)}K`;
      }
      return `${symbol}${numericAmount}`;
    }
  }

  // Standard Indian or International numbering format
  const locale = currency?.toUpperCase() === 'INR' ? 'en-IN' : 'en-US';
  const formattedNumber = new Intl.NumberFormat(locale, {
    maximumFractionDigits: 0,
  }).format(numericAmount);

  return `${symbol}${formattedNumber}`;
}
