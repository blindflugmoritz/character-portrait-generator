<script>
	import { onMount } from 'svelte';
	import { LAYERS, COLOR_PALETTES, getAssetPath } from './assetData.js';

	export let character = {};
	export let canvasSize = 512;

	let canvas;
	let ctx;
	let loadedImages = new Map();
	let isLoading = false;

	onMount(() => {
		ctx = canvas.getContext('2d');
		renderPortrait();
	});

	// Preload image and cache it
	async function loadImage(src) {
		if (loadedImages.has(src)) {
			return loadedImages.get(src);
		}

		return new Promise((resolve, reject) => {
			const img = new Image();
			img.onload = () => {
				loadedImages.set(src, img);
				resolve(img);
			};
			img.onerror = () => {
				console.warn(`Failed to load image: ${src}`);
				resolve(null);
			};
			img.src = src;
		});
	}

	// Apply color tint to an image
	function applyColorTint(img, hexColor) {
		// Create a temporary canvas for tinting
		const tempCanvas = document.createElement('canvas');
		tempCanvas.width = img.width;
		tempCanvas.height = img.height;
		const tempCtx = tempCanvas.getContext('2d');

		// Draw the original image
		tempCtx.drawImage(img, 0, 0);

		// Apply color overlay using multiply blend mode
		tempCtx.globalCompositeOperation = 'multiply';
		tempCtx.fillStyle = hexColor;
		tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

		// Restore original alpha
		tempCtx.globalCompositeOperation = 'destination-in';
		tempCtx.drawImage(img, 0, 0);

		return tempCanvas;
	}

	// Render the complete portrait
	async function renderPortrait() {
		if (!ctx || !character.parts) return;

		isLoading = true;

		// Clear canvas
		ctx.clearRect(0, 0, canvasSize, canvasSize);

		// Get color values
		const skinColor = character.colorIndices?.Skin !== undefined
			? COLOR_PALETTES.Skin[character.colorIndices.Skin]?.hex
			: COLOR_PALETTES.Skin[2].hex;
		const hairColor = character.colorIndices?.Hair !== undefined
			? COLOR_PALETTES.Hair[character.colorIndices.Hair]?.hex
			: COLOR_PALETTES.Hair[3].hex;
		const eyeColor = character.colorIndices?.Eye !== undefined
			? COLOR_PALETTES.Eye[character.colorIndices.Eye]?.hex
			: COLOR_PALETTES.Eye[2].hex;
		const accessoryColor = character.colorIndices?.Accessory !== undefined
			? COLOR_PALETTES.Accessory[character.colorIndices.Accessory]?.hex
			: COLOR_PALETTES.Accessory[1].hex;

		// Sort layers by ID (back to front: 20 to 0)
		const sortedLayers = Object.entries(LAYERS).sort((a, b) => b[1].id - a[1].id);

		for (const [layerName, layerInfo] of sortedLayers) {
			const partData = character.parts[layerName];

			if (!partData || partData.index === -1 || partData.variant === -1) {
				continue;
			}

			// Conditional logic: Skip mouth if moustache is present
			if (layerName === 'Mouth') {
				const moustache = character.parts.Moustache;
				if (moustache && moustache.index !== -1) {
					continue;
				}
			}

			const assetPath = getAssetPath(layerName, partData.index, partData.variant, character.gender || 'Male');
			if (!assetPath) {
				console.warn(`Invalid asset for ${layerName}: index ${partData.index}, variant ${partData.variant}, gender ${character.gender}`);
				continue;
			}

			const img = await loadImage(assetPath);
			if (img) {
				// Determine if we need to apply color tinting
				let renderImg = img;

				if (layerInfo.useSkinColor) {
					renderImg = applyColorTint(img, skinColor);
				} else if (layerInfo.useHairColor) {
					renderImg = applyColorTint(img, hairColor);
				} else if (layerInfo.useEyeColor) {
					renderImg = applyColorTint(img, eyeColor);
				} else if (layerInfo.useAccessoryColor) {
					renderImg = applyColorTint(img, accessoryColor);
				}

				// Calculate scaling to fit canvas while maintaining aspect ratio
				const scale = Math.min(canvasSize / renderImg.width, canvasSize / renderImg.height);
				const scaledWidth = renderImg.width * scale;
				const scaledHeight = renderImg.height * scale;
				const x = (canvasSize - scaledWidth) / 2;
				const y = (canvasSize - scaledHeight) / 2;

				ctx.drawImage(renderImg, x, y, scaledWidth, scaledHeight);
			}
		}

		isLoading = false;
	}

	// Export portrait as data URL
	export function exportPortrait() {
		return canvas.toDataURL('image/png');
	}

	// Watch for character changes and re-render
	$: if (character && ctx) {
		renderPortrait();
	}
</script>

<div class="portrait-container">
	<canvas
		bind:this={canvas}
		width={canvasSize}
		height={canvasSize}
		class="portrait-canvas"
		class:loading={isLoading}
	/>
	{#if isLoading}
		<div class="loading-overlay">
			<div class="spinner"></div>
		</div>
	{/if}
</div>

<style>
	.portrait-container {
		position: relative;
		display: inline-block;
		border: 2px solid #333;
		border-radius: 8px;
		overflow: hidden;
		background: #f5f5f5;
	}

	.portrait-canvas {
		display: block;
		image-rendering: pixelated;
		image-rendering: -moz-crisp-edges;
		image-rendering: crisp-edges;
	}

	.portrait-canvas.loading {
		opacity: 0.7;
	}

	.loading-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(255, 255, 255, 0.8);
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #f3f3f3;
		border-top: 4px solid #333;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
</style>
