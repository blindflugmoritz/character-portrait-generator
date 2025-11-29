// Portrait asset configuration based on character_data.js format

// Body shape options - metadata for game logic (not directly tied to sprite indices)
// Note: Only sprite indices 0 (Thin) and 1 (Average) exist, but all 4 can be selected
// The game uses this metadata; the closest matching sprite will be rendered
export const BODY_SHAPES = [
	{ index: 0, name: 'Thin' },
	{ index: 1, name: 'Average' },
	{ index: 2, name: 'Bulky' },
	{ index: 3, name: 'Fat' }
];

// Color palettes
export const COLOR_PALETTES = {
	Skin: [
		{ index: 0, name: 'Very Light', hex: '#FFE0BD' },
		{ index: 1, name: 'Light', hex: '#FFCD94' },
		{ index: 2, name: 'Light Medium', hex: '#EAC086' },
		{ index: 3, name: 'Medium', hex: '#C68642' },
		{ index: 4, name: 'Olive', hex: '#A67C52' },
		{ index: 5, name: 'Brown', hex: '#8D5524' },
		{ index: 6, name: 'Dark Brown', hex: '#664229' }
	],
	Hair: [
		{ index: 0, name: 'Platinum Blonde', hex: '#F5F5DC' },
		{ index: 1, name: 'Blonde', hex: '#E5C18A' },
		{ index: 2, name: 'Light Brown', hex: '#A67C52' },
		{ index: 3, name: 'Brown', hex: '#6E4A2D' },
		{ index: 4, name: 'Dark Brown', hex: '#4A2C1C' },
		{ index: 5, name: 'Black', hex: '#1C1C1C' },
		{ index: 6, name: 'Auburn', hex: '#8B4513' },
		{ index: 7, name: 'Red', hex: '#C85A32' }
	],
	Eye: [
		{ index: 0, name: 'Blue', hex: '#5A9BCF' },
		{ index: 1, name: 'Green', hex: '#5FA777' },
		{ index: 2, name: 'Brown', hex: '#6E4A2D' },
		{ index: 3, name: 'Hazel', hex: '#8D6E49' },
		{ index: 4, name: 'Gray', hex: '#8FA8B0' },
		{ index: 5, name: 'Amber', hex: '#D4A650' }
	],
	Accessory: [
		{ index: 0, name: 'Black', hex: '#1C1C1C' },
		{ index: 1, name: 'Brown', hex: '#6E4A2D' },
		{ index: 2, name: 'Gray', hex: '#808080' },
		{ index: 3, name: 'Silver', hex: '#C0C0C0' },
		{ index: 4, name: 'Gold', hex: '#FFD700' }
	]
};

// Layer definitions (render order: 20 to 0, back to front)
export const LAYERS = {
	Background: { id: 20, folder: '20_Background_Background', category: 'Background', canBeNone: true },
	ClothesBack: { id: 19, folder: '19_ClothesBack_Clothes', category: 'Clothes', canBeNone: false },
	HairBack: { id: 18, folder: '18_HairBack_Hair', category: 'Hair', canBeNone: true, useHairColor: true },
	Body: { id: 17, folder: '17_Body_Skin', category: 'Skin', canBeNone: false, useSkinColor: true },
	Clothes: { id: 16, folder: '16_Clothes_Clothes', category: 'Clothes', canBeNone: false },
	Ears: { id: 15, folder: '15_Ears_Skin', category: 'Skin', canBeNone: false, useSkinColor: true },
	AccessoryHead: { id: 14, folder: '14_Accessory_Accessory', category: 'Accessory', canBeNone: true, useAccessoryColor: true },
	Headshape: { id: 13, folder: '13_Headshape_Skin', category: 'Skin', canBeNone: false, useSkinColor: true },
	DetailUpper: { id: 12, folder: '12_Detail_Skin', category: 'Skin', canBeNone: true, useSkinColor: true },
	DetailLower: { id: 11, folder: '11_Detail_Skin', category: 'Skin', canBeNone: true, useSkinColor: true },
	Hair: { id: 10, folder: '10_Hair_Hair', category: 'Hair', canBeNone: false, useHairColor: true },
	Mouth: { id: 9, folder: '9_Mouth_Lip', category: 'Lip', canBeNone: true },
	Beard: { id: 8, folder: '8_Beard_Hair', category: 'Hair', canBeNone: true, useHairColor: true },
	Moustache: { id: 7, folder: '7_Moustache_Hair', category: 'Hair', canBeNone: true, useHairColor: true },
	// HeadAuxiliary: Not implemented in game, layer 6 removed from UI
	Eyes: { id: 5, folder: '5_Eyes_Eye', category: 'Eye', canBeNone: false, useEyeColor: true },
	Eyebrows: { id: 4, folder: '4_Eyebrows_Hair', category: 'Hair', canBeNone: false, useHairColor: true },
	AccessoryFace: { id: 3, folder: '3_Accessory_Accessory', category: 'Accessory', canBeNone: true, useAccessoryColor: true },
	Nose: { id: 2, folder: '2_Nose_Skin', category: 'Skin', canBeNone: false, useSkinColor: true },
	Blemish: { id: 1, folder: '1_Blemish_Skin', category: 'Skin', canBeNone: true, useSkinColor: true },
	AccessoryFront: { id: 0, folder: '0_Accessory_Accessory', category: 'Accessory', canBeNone: true, useAccessoryColor: true }
};

// Asset index/variant mappings based on character_data.js valid combinations
// Format: { index: variantCount } where variantCount = number of valid variants starting from 0
// OR { index: [array of valid variants] } for non-consecutive variants
export const ASSET_VARIANTS = {
	'Accessory': {
		variants: { 0: 4, 1: 1, 2: 4, 3: 1 }  // Index 0: variants 0-3, Index 1: variant 0, etc.
	},
	'Beard': {
		variants: { 0: 3, 20: 1 }  // Index 0: variants 0-2, Index 20: variant 0
	},
	'Blemish': {
		variants: { 0: 1, 1: 1, 2: 1 }  // All indices: variant 0 only
	},
	'Body': {
		variants: { 0: 1, 1: 1 }  // Both indices: variant 0 only
	},
	'Clothes': {
		variants: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1 },
		femaleOnlyIndices: [7, 8, 9, 10, 11, 12],  // These indices only exist with _F.png suffix
		femaleSuffix: '_F.png'  // Clothes uses _F.png instead of _female.png
	},
	'ClothesBack': {
		variants: { 0: 1, 14: 1 }
	},
	'Detail': {
		// Indices 0-20 all have variant 0 only
		variants: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 20: 1 }
	},
	'Ears': {
		// Indices 0-7 all have variant 0 only
		variants: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1 }
	},
	'Eyebrows': {
		variants: { 0: 2, 1: 1, 2: 2, 3: 2, 4: 1, 5: 3, 6: 2, 7: 1 }
	},
	'Eyes': {
		// Note: Index 9 has gender-specific sprites (M+F), others are M only
		variants: { 0: 2, 1: 1, 2: 1, 3: 6, 4: 2, 5: 1, 6: 1, 7: 2, 8: 4, 9: 2, 10: 1, 11: 1, 12: 2 },
		genderSpecific: { 9: true }  // Index 9 has both base and _female sprites
	},
	'Hair': {
		// Indices with (M+F) notation have gender-specific sprites: 7, 8, 9, 10
		// F-only variants: 7 (variants 2,3), 9 (variants 2,3)
		variants: { 0: 3, 1: 2, 2: 3, 3: 3, 4: 1, 5: 2, 6: 3, 7: 4, 8: 2, 9: 4, 10: 2, 11: 2, 12: 1, 13: 1 },
		genderSpecific: { 7: true, 8: true, 9: true, 10: true },
		femaleOnlyVariants: { 7: [2, 3], 9: [2, 3] }  // These variants only exist as _female
	},
	'HairBack': {
		// Index 7 has only female variants (0, 1, 3 - note: variant 2 missing, so using array)
		// Index 9 has variants 4,5 as female-only
		variants: { 4: 1, 7: [0, 1, 3], 8: 2, 9: 6, 10: 2, 11: 2, 12: 2, 13: 1 },
		femaleOnlyIndices: [7],  // Index 7 only exists as female
		genderSpecific: { 8: true, 9: true, 10: true },
		femaleOnlyVariants: { 9: [4, 5] }  // Index 9 variants 4,5 are female-only
	},
	// 'HeadAuxiliary': removed - not implemented in game
	'Headshape': {
		// Index 8 and 9 have gender-specific sprites
		variants: { 0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 2, 8: 3, 9: 2, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1 },
		genderSpecific: { 8: true, 9: true },
		femaleOnlyVariants: { 9: [1] }  // Index 9 variant 1 is female-only
	},
	'Moustache': {
		variants: { 0: 2, 1: 2, 2: 2, 3: 3, 4: 3 }
	},
	'Mouth': {
		// Indices 0-15 all have variant 0 only
		variants: { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1 }
	},
	'Nose': {
		variants: { 0: 3, 1: 2, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 1, 11: 1, 12: 2, 20: 1, 21: 1 }
	},
	'Background': {
		variants: { 0: 1, 1: 1, 2: 1, 3: 1 }  // 0-2: custom backgrounds, 3: white background, None option available via canBeNone
	}
};

// Map layer names to asset variant keys
const LAYER_TO_VARIANT_KEY = {
	'AccessoryFront': 'Accessory',
	'AccessoryFace': 'Accessory',
	'AccessoryHead': 'Accessory',
	'Blemish': 'Blemish',
	'Nose': 'Nose',
	'Eyebrows': 'Eyebrows',
	'Eyes': 'Eyes',
	'Moustache': 'Moustache',
	'Beard': 'Beard',
	'Mouth': 'Mouth',
	'Hair': 'Hair',
	'HairBack': 'HairBack',
	'DetailUpper': 'Detail',
	'DetailLower': 'Detail',
	'Headshape': 'Headshape',
	// 'HeadAuxiliary': removed - not implemented in game
	'Ears': 'Ears',
	'Clothes': 'Clothes',
	'ClothesBack': 'ClothesBack',
	'Body': 'Body',
	'Background': 'Background'
};

// Clothes to ClothesBack dependency mapping
// Maps Clothes index to the required ClothesBack index
export const CLOTHES_BACK_MAPPING = {
	0: 0,   // clothes_00_00 → clothesback_00_00
	1: 14   // clothes_01_00 → clothesback_14_00
	// Add more mappings here as needed
};

/**
 * Get asset filename from index and variant
 * @param {string} layerName
 * @param {number} index
 * @param {number} variant
 * @param {string} gender
 * @returns {string | null}
 */
export function getAssetFilename(layerName, index, variant, gender = 'Male') {
	if (index === -1 || variant === -1) return null;

	const layer = LAYERS[layerName];
	if (!layer) return null;

	// Extract the base name from folder (e.g., '10_Hair_Hair' -> 'hair')
	const parts = layer.folder.split('_');
	const baseName = parts[1].toLowerCase();

	const baseFilename = `${baseName}_${String(index).padStart(2, '0')}_${String(variant).padStart(2, '0')}`;

	const variantKey = LAYER_TO_VARIANT_KEY[layerName];
	const assetData = ASSET_VARIANTS[variantKey];

	// Check for female-only indices (e.g., Clothes 7-12, HairBack 7)
	if (assetData?.femaleOnlyIndices?.includes(index)) {
		if (gender === 'Female') {
			// Use custom suffix if defined, otherwise default to _female.png
			if (assetData.femaleSuffix) {
				return `${baseFilename}${assetData.femaleSuffix}`;
			}
			return `${baseFilename}_female.png`;
		}
		// Male shouldn't access female-only indices
		return null;
	}

	// Check if this is a gender-specific sprite that needs gender suffix
	if (gender === 'Female' && assetData?.genderSpecific?.[index]) {
		if (assetData.femaleSuffix) {
			return `${baseFilename}${assetData.femaleSuffix}`;
		}
		return `${baseFilename}_female.png`;
	}

	return `${baseFilename}.png`;
}

/**
 * Get full asset path
 * @param {string} layerName
 * @param {number} index
 * @param {number} variant
 * @param {string} gender
 * @returns {string | null}
 */
export function getAssetPath(layerName, index, variant, gender = 'Male') {
	const filename = getAssetFilename(layerName, index, variant, gender);
	if (!filename) return null;

	const layer = LAYERS[layerName];
	let folder = layer.folder;

	// Special cases for shared asset directories:

	// All accessory layers (0, 3, 14) share the same assets from folder 3
	if (layerName === 'AccessoryFront' || layerName === 'AccessoryHead') {
		folder = '3_Accessory_Accessory';
	}

	// Detail layers are split: indices 0-9 in folder 11, indices 10-20 in folder 12
	if (layerName === 'DetailLower' || layerName === 'DetailUpper') {
		if (index >= 0 && index <= 9) {
			folder = '11_Detail_Skin';
		} else if (index >= 10 && index <= 20) {
			folder = '12_Detail_Skin';
		}
	}

	// Use VITE_STATIC_BASE_PATH env var for production (defaults to '' for SvelteKit dev)
	const basePath = import.meta.env.VITE_STATIC_BASE_PATH || '';
	return `${basePath}/PortraitSprites/${folder}/${filename}`;
}

/**
 * Get available indices for a layer
 * @param {string} layerName
 * @param {string | null} gender - Optional gender filter
 * @returns {number[]}
 */
export function getAvailableIndices(layerName, gender = null) {
	const variantKey = LAYER_TO_VARIANT_KEY[layerName];
	const assetData = ASSET_VARIANTS[variantKey];

	if (!assetData || !assetData.variants) return [];

	let indices = Object.keys(assetData.variants).map(Number).sort((a, b) => a - b);

	// Filter out female-only indices for Male characters
	if (gender === 'Male' && assetData.femaleOnlyIndices) {
		indices = indices.filter(idx => !assetData.femaleOnlyIndices.includes(idx));
	}

	return indices;
}

/**
 * Get available variants for a specific index
 * Optionally respects gender restrictions for gender-specific sprites
 * @param {string} layerName
 * @param {number} index
 * @param {string | null} gender
 * @returns {number[]}
 */
export function getAvailableVariants(layerName, index, gender = null) {
	const variantKey = LAYER_TO_VARIANT_KEY[layerName];
	const assetData = ASSET_VARIANTS[variantKey];

	if (!assetData || !assetData.variants[index]) return [];

	const variantData = assetData.variants[index];
	let variants;

	// Handle both array format [0, 1, 3] and number format (3 = 0,1,2)
	if (Array.isArray(variantData)) {
		variants = [...variantData];
	} else {
		variants = Array.from({ length: variantData }, (_, i) => i);
	}

	// Filter out female-only variants if gender is Male
	if (gender === 'Male' && assetData.femaleOnlyVariants?.[index]) {
		const femaleOnly = assetData.femaleOnlyVariants[index];
		variants = variants.filter(v => !femaleOnly.includes(v));
	}

	return variants;
}

/**
 * Get matching HairBack indices for a given Hair index
 * HairBack sprites match Hair sprites by their identification number (first number)
 * @param {number} hairIndex - The Hair index (e.g., 7 from hair_07_00)
 * @param {string} gender
 * @returns {number[]} - Array of matching HairBack indices, empty if none exist
 */
export function getMatchingHairBackIndices(hairIndex, gender = null) {
	const hairBackIndices = getAvailableIndices('HairBack', gender);
	// Only return HairBack indices that match the Hair index
	return hairBackIndices.filter(idx => idx === hairIndex);
}

/**
 * Check if a variant is valid for the given gender
 * @param {string} layerName
 * @param {number} index
 * @param {number} variant
 * @param {string} gender
 * @returns {boolean}
 */
export function isValidVariantForGender(layerName, index, variant, gender) {
	const variantKey = LAYER_TO_VARIANT_KEY[layerName];
	const assetData = ASSET_VARIANTS[variantKey];

	if (!assetData) return false;

	const variantData = assetData.variants[index];
	if (!variantData) return false;

	// Check if variant exists (handle both array and number formats)
	if (Array.isArray(variantData)) {
		if (!variantData.includes(variant)) return false;
	} else {
		if (variant >= variantData) return false;
	}

	// Check gender restrictions
	if (gender === 'Male' && assetData.femaleOnlyVariants?.[index]?.includes(variant)) {
		return false;
	}

	return true;
}

/**
 * Generate random character data
 * @param {string} gender
 * @param {object} options - Optional constraints { skinColorRange: [min, max] }
 * @returns {object}
 */
export function generateRandomCharacter(gender = 'Male', options = {}) {
	const { skinColorRange = [0, COLOR_PALETTES.Skin.length - 1] } = options;

	// Pick random skin color within allowed range
	const minSkin = Math.max(0, skinColorRange[0]);
	const maxSkin = Math.min(COLOR_PALETTES.Skin.length - 1, skinColorRange[1]);
	const skinColorIndex = minSkin + Math.floor(Math.random() * (maxSkin - minSkin + 1));

	const character = {
		gender: gender,
		bodyShapeIndex: Math.floor(Math.random() * BODY_SHAPES.length),
		colorIndices: {
			Skin: skinColorIndex,
			Hair: Math.floor(Math.random() * COLOR_PALETTES.Hair.length),
			Eye: Math.floor(Math.random() * COLOR_PALETTES.Eye.length),
			Accessory: Math.floor(Math.random() * COLOR_PALETTES.Accessory.length)
		},
		parts: {}
	};

	// First pass: Add each layer (except Mouth, ClothesBack, and HairBack which have dependencies)
	for (const [layerName, layer] of Object.entries(LAYERS)) {
		if (layerName === 'Mouth' || layerName === 'ClothesBack' || layerName === 'HairBack') continue; // Handle dependent layers separately

		// Skip facial hair for females
		if (gender === 'Female' && (layerName === 'Beard' || layerName === 'Moustache')) {
			character.parts[layerName] = { index: -1, variant: -1 };
			continue;
		}

		// Required layers always get a value
		if (!layer.canBeNone || Math.random() > 0.3) {
			const indices = getAvailableIndices(layerName, gender);
			if (indices.length > 0) {
				const randomIndex = indices[Math.floor(Math.random() * indices.length)];
				const variants = getAvailableVariants(layerName, randomIndex, gender);
				if (variants.length > 0) {
					const randomVariant = variants[Math.floor(Math.random() * variants.length)];
					character.parts[layerName] = { index: randomIndex, variant: randomVariant };
				}
			}
		} else {
			character.parts[layerName] = { index: -1, variant: -1 };
		}
	}

	// Handle ClothesBack: Set based on Clothes selection
	const clothesIndex = character.parts.Clothes?.index;
	if (clothesIndex !== undefined && clothesIndex !== -1) {
		const clothesBackIndex = CLOTHES_BACK_MAPPING[clothesIndex];
		if (clothesBackIndex !== undefined) {
			character.parts.ClothesBack = { index: clothesBackIndex, variant: 0 };
		} else {
			// If no mapping exists, set a random ClothesBack
			const indices = getAvailableIndices('ClothesBack', gender);
			if (indices.length > 0) {
				const randomIndex = indices[Math.floor(Math.random() * indices.length)];
				character.parts.ClothesBack = { index: randomIndex, variant: 0 };
			}
		}
	} else {
		character.parts.ClothesBack = { index: -1, variant: -1 };
	}

	// Handle Mouth: Only add if Moustache is -1
	const hasMoustache = character.parts.Moustache?.index !== -1;
	if (!hasMoustache) {
		// Mouth can be present (70% chance) when no moustache
		if (Math.random() > 0.3) {
			const indices = getAvailableIndices('Mouth', gender);
			if (indices.length > 0) {
				const randomIndex = indices[Math.floor(Math.random() * indices.length)];
				const variants = getAvailableVariants('Mouth', randomIndex, gender);
				if (variants.length > 0) {
					const randomVariant = variants[Math.floor(Math.random() * variants.length)];
					character.parts.Mouth = { index: randomIndex, variant: randomVariant };
				}
			}
		} else {
			character.parts.Mouth = { index: -1, variant: -1 };
		}
	} else {
		// Must be -1 if moustache exists
		character.parts.Mouth = { index: -1, variant: -1 };
	}

	// Handle HairBack: Set based on Hair selection (matching identification numbers)
	const hairIndex = character.parts.Hair?.index;
	if (hairIndex !== undefined && hairIndex !== -1) {
		const matchingHairBackIndices = getMatchingHairBackIndices(hairIndex, gender);
		if (matchingHairBackIndices.length > 0 && Math.random() > 0.3) {
			// 70% chance to add matching HairBack if available
			const randomIndex = matchingHairBackIndices[Math.floor(Math.random() * matchingHairBackIndices.length)];
			const variants = getAvailableVariants('HairBack', randomIndex, gender);
			if (variants.length > 0) {
				const randomVariant = variants[Math.floor(Math.random() * variants.length)];
				character.parts.HairBack = { index: randomIndex, variant: randomVariant };
			} else {
				character.parts.HairBack = { index: -1, variant: -1 };
			}
		} else {
			// No matching HairBack or 30% chance to skip
			character.parts.HairBack = { index: -1, variant: -1 };
		}
	} else {
		// No hair selected
		character.parts.HairBack = { index: -1, variant: -1 };
	}

	return character;
}

/**
 * Create default character
 * @param {string} gender
 * @returns {object}
 */
export function createDefaultCharacter(gender = 'Male') {
	return {
		gender: gender,
		bodyShapeIndex: 1, // Average
		colorIndices: {
			Skin: 2,
			Hair: 3,
			Eye: 2,
			Accessory: 1
		},
		parts: {
			Body: { index: 0, variant: 0 },
			Headshape: { index: 0, variant: 0 },
			Ears: { index: 0, variant: 0 },
			Eyes: { index: 0, variant: 0 },
			Nose: { index: 0, variant: 0 },
			Mouth: { index: 0, variant: 0 },
			Eyebrows: { index: 0, variant: 0 },
			Hair: { index: 0, variant: 0 },
			HairBack: { index: 4, variant: 0 },
			Clothes: { index: 0, variant: 0 },
			ClothesBack: { index: 0, variant: 0 }
		}
	};
}
