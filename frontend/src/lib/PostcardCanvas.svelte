<script>
	import { onMount } from 'svelte';
	import { LAYERS, COLOR_PALETTES, getAssetPath } from './assetData.js';

	/**
	 * @type {'blue' | 'orange'}
	 */
	export let color = 'blue';

	/**
	 * @type {string}
	 */
	export let templatePath;

	/**
	 * @type {Array<{x: number, y: number, width: number, height: number}>}
	 */
	export let slots;

	/**
	 * @type {Array<Object>}
	 */
	export let characters = [];

	let canvas;
	let ctx;
	let loadedTemplateImage = null;
	let loadedPortraitImages = new Map();
	let isRendering = false;

	// Canvas dimensions - we'll match the template size
	const CANVAS_WIDTH = 1024;
	const CANVAS_HEIGHT = 614;

	onMount(() => {
		ctx = canvas.getContext('2d');
		loadTemplateImage();
	});

	/**
	 * Load the postcard template image
	 */
	async function loadTemplateImage() {
		const img = new Image();
		img.onload = () => {
			loadedTemplateImage = img;
			renderPostcard();
		};
		img.onerror = () => {
			console.error('Failed to load template:', templatePath);
		};
		img.src = templatePath;
	}

	/**
	 * Cache for tinted images
	 */
	const tintedImageCache = new Map();

	/**
	 * Apply color tint to an image with caching
	 * Uses the same method as PortraitCanvas.svelte for consistency
	 */
	function applyColorTint(img, hexColor) {
		const cacheKey = `${img.src}_${hexColor}`;

		if (tintedImageCache.has(cacheKey)) {
			return tintedImageCache.get(cacheKey);
		}

		const tintCanvas = document.createElement('canvas');
		tintCanvas.width = img.width;
		tintCanvas.height = img.height;
		const tintCtx = tintCanvas.getContext('2d');

		// Draw the original image
		tintCtx.drawImage(img, 0, 0);

		// Apply color overlay using multiply blend mode
		tintCtx.globalCompositeOperation = 'multiply';
		tintCtx.fillStyle = hexColor;
		tintCtx.fillRect(0, 0, tintCanvas.width, tintCanvas.height);

		// Restore original alpha
		tintCtx.globalCompositeOperation = 'destination-in';
		tintCtx.drawImage(img, 0, 0);

		tintedImageCache.set(cacheKey, tintCanvas);
		return tintCanvas;
	}

	/**
	 * Cache for rendered characters
	 */
	const characterCanvasCache = new Map();

	/**
	 * Load a character portrait onto a temporary canvas
	 */
	async function renderCharacterToCanvas(character) {
		// Create cache key from character data
		const cacheKey = JSON.stringify({
			parts: character.parts,
			colors: character.colorIndices,
			gender: character.gender
		});

		// Return cached canvas if available
		if (characterCanvasCache.has(cacheKey)) {
			return characterCanvasCache.get(cacheKey);
		}

		// Create a temporary canvas for this character
		const tempCanvas = document.createElement('canvas');
		tempCanvas.width = 256; // Reduced resolution for better performance
		tempCanvas.height = 256;
		const tempCtx = tempCanvas.getContext('2d', {
			willReadFrequently: false,
			alpha: true
		});

		// Get color values
		const skinColor =
			character.colorIndices?.Skin !== undefined
				? COLOR_PALETTES.Skin[character.colorIndices.Skin]?.hex
				: COLOR_PALETTES.Skin[2].hex;
		const hairColor =
			character.colorIndices?.Hair !== undefined
				? COLOR_PALETTES.Hair[character.colorIndices.Hair]?.hex
				: COLOR_PALETTES.Hair[3].hex;
		const eyeColor =
			character.colorIndices?.Eye !== undefined
				? COLOR_PALETTES.Eye[character.colorIndices.Eye]?.hex
				: COLOR_PALETTES.Eye[2].hex;
		const accessoryColor =
			character.colorIndices?.Accessory !== undefined
				? COLOR_PALETTES.Accessory[character.colorIndices.Accessory]?.hex
				: COLOR_PALETTES.Accessory[1].hex;

		// Sort layers by ID (back to front)
		const sortedLayers = Object.entries(LAYERS).sort((a, b) => b[1].id - a[1].id);

		for (const [layerName, layerInfo] of sortedLayers) {
			const partData = character.parts[layerName];

			if (!partData || partData.index === -1 || partData.variant === -1) {
				continue;
			}

			// Skip mouth if moustache is present
			if (layerName === 'Mouth') {
				const moustache = character.parts.Moustache;
				if (moustache && moustache.index !== -1) {
					continue;
				}
			}

			const assetPath = getAssetPath(
				layerName,
				partData.index,
				partData.variant,
				character.gender || 'Male'
			);

			if (!assetPath) continue;

			const img = await loadImage(assetPath);
			if (img) {
				let renderImg = img;

				// Apply color tinting based on layer type
				if (layerInfo.useSkinColor) {
					renderImg = applyColorTint(img, skinColor);
				} else if (layerInfo.useHairColor) {
					renderImg = applyColorTint(img, hairColor);
				} else if (layerInfo.useEyeColor) {
					renderImg = applyColorTint(img, eyeColor);
				} else if (layerInfo.useAccessoryColor) {
					renderImg = applyColorTint(img, accessoryColor);
				}

				tempCtx.drawImage(renderImg, 0, 0, 256, 256);
			}
		}

		// Cache the rendered canvas
		characterCanvasCache.set(cacheKey, tempCanvas);

		// Limit cache size to prevent memory issues
		if (characterCanvasCache.size > 20) {
			const firstKey = characterCanvasCache.keys().next().value;
			characterCanvasCache.delete(firstKey);
		}

		return tempCanvas;
	}

	/**
	 * Load an image and cache it
	 */
	function loadImage(path) {
		return new Promise((resolve) => {
			if (loadedPortraitImages.has(path)) {
				resolve(loadedPortraitImages.get(path));
				return;
			}

			const img = new Image();
			img.onload = () => {
				loadedPortraitImages.set(path, img);
				resolve(img);
			};
			img.onerror = () => {
				console.error('Failed to load image:', path);
				resolve(null);
			};
			img.src = path;
		});
	}

	/**
	 * Render the complete postcard
	 */
	async function renderPostcard() {
		if (!ctx || !loadedTemplateImage || isRendering) return;

		isRendering = true;

		try {
			// Clear canvas
			ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

			// Draw template
			ctx.drawImage(loadedTemplateImage, 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

			// Draw each character in their slot
			for (let i = 0; i < characters.length && i < slots.length; i++) {
				const character = characters[i];
				const slot = slots[i];

				if (character && Object.keys(character).length > 0) {
					const characterCanvas = await renderCharacterToCanvas(character);

					// Calculate slot position and size in pixels
					const slotX = (slot.x / 100) * CANVAS_WIDTH;
					const slotY = (slot.y / 100) * CANVAS_HEIGHT;
					const slotWidth = (slot.width / 100) * CANVAS_WIDTH;
					const slotHeight = (slot.height / 100) * CANVAS_HEIGHT;

					// Make the slot square (use width as dimension to match template)
					const squareSize = slotWidth;

					// Draw background box with cream/beige color
					ctx.fillStyle = '#EDE7DD';
					ctx.fillRect(slotX, slotY, squareSize, squareSize);

					// Draw subtle shadow/border
					ctx.strokeStyle = '#C8BFB0';
					ctx.lineWidth = 3;
					ctx.strokeRect(slotX, slotY, squareSize, squareSize);

					// Draw character portrait with slight padding
					const padding = 4;
					ctx.drawImage(
						characterCanvas,
						slotX + padding,
						slotY + padding,
						squareSize - padding * 2,
						squareSize - padding * 2
					);
				}
			}
		} catch (error) {
			console.error('Error rendering postcard:', error);
		} finally {
			isRendering = false;
		}
	}

	/**
	 * Export the postcard as PNG
	 */
	export function exportPostcard() {
		if (!canvas) return null;
		return canvas.toDataURL('image/png');
	}

	// Re-render when inputs change
	$: if (ctx && templatePath) {
		loadTemplateImage();
	}

	$: if (ctx && loadedTemplateImage && (characters || slots)) {
		renderPostcard();
	}
</script>

<canvas
	bind:this={canvas}
	width={CANVAS_WIDTH}
	height={CANVAS_HEIGHT}
	class="postcard-canvas"
></canvas>

<style>
	.postcard-canvas {
		max-width: 100%;
		height: auto;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background: white;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}
</style>
