/**
 * Postcard template configurations and character slot positions
 * Based on "Ground of Aces" promotional postcard designs
 */

// Base slot positions for the 10-character crew layout
// Positions are in percentages relative to template dimensions
// Template dimensions: ~1024px width (blue), ~1024px width (orange crew)
const BASE_SLOTS = [
	// Top row - 7 slots (left to right)
	{ x: 5.5, y: 5.5, width: 13.0, height: 26.0 },   // Slot 1
	{ x: 19.5, y: 5.5, width: 13.0, height: 26.0 },  // Slot 2
	{ x: 33.5, y: 5.5, width: 13.0, height: 26.0 },  // Slot 3
	{ x: 47.5, y: 5.5, width: 13.0, height: 26.0 },  // Slot 4
	{ x: 61.5, y: 5.5, width: 13.0, height: 26.0 },  // Slot 5
	{ x: 75.5, y: 5.5, width: 13.0, height: 26.0 },  // Slot 6
	{ x: 89.5, y: 5.5, width: 13.0, height: 26.0 },  // Slot 7
	// Bottom row - 3 slots (left to right)
	{ x: 5.5, y: 33.0, width: 13.0, height: 26.0 },  // Slot 8
	{ x: 19.5, y: 33.0, width: 13.0, height: 26.0 }, // Slot 9
	{ x: 33.5, y: 33.0, width: 13.0, height: 26.0 }  // Slot 10
];

// Single character position for blue postcard (top-left large portrait)
const SINGLE_SLOT_BLUE = {
	x: 5.5,
	y: 9.0,
	width: 28.0,
	height: 52.0
};

/**
 * Get character slots for a specific count (1-10)
 * @param {number} count - Number of characters (1-10)
 * @returns {Array} Array of slot position objects
 */
export function getCharacterSlots(count) {
	if (count < 1 || count > 10) {
		throw new Error('Character count must be between 1 and 10');
	}

	// Return the first N slots from BASE_SLOTS (left to right, top to bottom)
	return BASE_SLOTS.slice(0, count);
}

/**
 * Postcard template configurations
 */
export const POSTCARD_TEMPLATES = {
	blue: {
		name: 'R.A.F. Lichfield',
		templatePath: '/PostcardTemplates/goa_postcard_greetingsfromlichfield_noboxes_720.png',
		bgColor: '#3A9BB5',
		// Single character uses a different, larger position
		singleSlot: SINGLE_SLOT_BLUE
	},
	orange: {
		name: 'Lichfield Crew',
		templatePath: '/PostcardTemplates/goa_postcard_greetingsfromlichfieldcrew_noboxes.png',
		bgColor: '#E67E22'
	}
};

/**
 * Get postcard configuration for a specific color and character count
 * @param {string} color - 'blue' or 'orange'
 * @param {number} characterCount - Number of characters (1-10)
 * @returns {Object} Postcard configuration with template and slots
 */
export function getPostcardConfig(color, characterCount) {
	const template = POSTCARD_TEMPLATES[color];
	if (!template) {
		throw new Error(`Invalid color: ${color}. Must be 'blue' or 'orange'`);
	}

	// For blue single character, use the large single slot
	if (color === 'blue' && characterCount === 1) {
		return {
			...template,
			slots: [template.singleSlot]
		};
	}

	// For all other cases, use the grid layout
	return {
		...template,
		slots: getCharacterSlots(characterCount)
	};
}
