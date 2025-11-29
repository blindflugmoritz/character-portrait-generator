<script>
	import {
		LAYERS,
		BODY_SHAPES,
		COLOR_PALETTES,
		getAvailableIndices,
		getAvailableVariants,
		getAssetFilename,
		generateRandomCharacter,
		createDefaultCharacter,
		CLOTHES_BACK_MAPPING,
		getMatchingHairBackIndices
	} from './assetData.js';
	import { spriteLabels } from './spriteLabels.js';

	export let character = {};

	// Initialize with default character if empty
	if (!character.parts) {
		character = createDefaultCharacter();
	}

	// Ensure gender exists
	if (!character.gender) {
		character.gender = 'Male';
	}


	// Randomize character
	function randomizeCharacter() {
		character = generateRandomCharacter(character.gender);
	}

	// Update gender - regenerate random character with new gender
	function updateGender(newGender) {
		console.log('Gender changed to:', newGender, '- generating new random character');
		character = generateRandomCharacter(newGender);
	}

	// Update part
	function updatePart(layerName, index, variant) {
		const newParts = {
			...character.parts,
			[layerName]: { index: parseInt(index), variant: parseInt(variant) }
		};

		// If setting Moustache to a value (not -1), clear Mouth
		if (layerName === 'Moustache' && parseInt(index) !== -1) {
			newParts.Mouth = { index: -1, variant: -1 };
		}

		// If setting Clothes, automatically set ClothesBack based on mapping
		if (layerName === 'Clothes') {
			const clothesIndex = parseInt(index);
			const clothesBackIndex = CLOTHES_BACK_MAPPING[clothesIndex];
			if (clothesBackIndex !== undefined) {
				newParts.ClothesBack = { index: clothesBackIndex, variant: 0 };
			}
		}

		// If setting Hair, update HairBack to match or clear if no match exists
		if (layerName === 'Hair') {
			const hairIndex = parseInt(index);
			if (hairIndex !== -1) {
				const matchingHairBackIndices = getMatchingHairBackIndices(hairIndex, character.gender);
				const currentHairBack = character.parts.HairBack?.index;

				// If current HairBack doesn't match new Hair, clear it or set to first matching
				if (!matchingHairBackIndices.includes(currentHairBack)) {
					if (matchingHairBackIndices.length > 0) {
						// Set to first matching HairBack
						newParts.HairBack = { index: matchingHairBackIndices[0], variant: 0 };
					} else {
						// No matching HairBack exists, clear it
						newParts.HairBack = { index: -1, variant: -1 };
					}
				}
			} else {
				// Hair removed, clear HairBack
				newParts.HairBack = { index: -1, variant: -1 };
			}
		}

		character = {
			...character,
			parts: newParts
		};
	}

	// Remove part (set to -1)
	function removePart(layerName) {
		character = {
			...character,
			parts: {
				...character.parts,
				[layerName]: { index: -1, variant: -1 }
			}
		};
	}

	// Update color
	function updateColor(colorType, colorIndex) {
		character = {
			...character,
			colorIndices: {
				...character.colorIndices,
				[colorType]: parseInt(colorIndex)
			}
		};
	}

	// Update body shape
	function updateBodyShape(shapeIndex) {
		character = {
			...character,
			bodyShapeIndex: parseInt(shapeIndex)
		};
	}

	// Get layers grouped by category
	$: layersByCategory = Object.entries(LAYERS).reduce((acc, [name, layer]) => {
		if (!acc[layer.category]) {
			acc[layer.category] = [];
		}
		acc[layer.category].push({ name, ...layer });
		return acc;
	}, {});

	// Sort categories with Background at the end
	$: sortedCategories = Object.entries(layersByCategory).sort(([catA], [catB]) => {
		if (catA === 'Background') return 1;
		if (catB === 'Background') return -1;
		return 0;
	});

	// Helper: Get sprite label from layer, index, variant
	function getSpriteLabel(layerName, index, variant) {
		// Try to get label without gender suffix first (base sprite name)
		const baseFilename = getAssetFilename(layerName, index, variant, 'Male');
		if (!baseFilename) return 'Unknown';

		const layer = LAYERS[layerName];
		const folder = layer.folder;

		// Look up label using base filename (labels are stored without _female suffix)
		return spriteLabels[folder]?.[baseFilename] || `${layerName} ${index}`;
	}
</script>

<div class="controls-container">
	<div class="controls-header">
		<h2>Character Customization</h2>
		<button class="randomize-btn" on:click={randomizeCharacter}>🎲 Randomize</button>
	</div>

	<!-- Gender Selection -->
	<div class="section">
		<h3>Gender</h3>
		<select
			value={character.gender}
			on:change={(e) => {
				console.log('Gender dropdown changed to:', e.target.value);
				updateGender(e.target.value);
			}}
		>
			<option value="Male">Male</option>
			<option value="Female">Female</option>
		</select>
	</div>

	<!-- Body Shape Selection -->
	<div class="section">
		<h3>Body Shape</h3>
		<select
			value={character.bodyShapeIndex}
			on:change={(e) => updateBodyShape(e.target.value)}
		>
			{#each BODY_SHAPES as shape}
				<option value={shape.index}>{shape.name}</option>
			{/each}
		</select>
	</div>

	<!-- Color Selection -->
	<div class="section">
		<h3>Colors</h3>
		<div class="color-controls">
			<div class="color-control">
				<label>Skin Color</label>
				<select
					value={character.colorIndices?.Skin ?? 2}
					on:change={(e) => updateColor('Skin', e.target.value)}
				>
					{#each COLOR_PALETTES.Skin as color}
						<option value={color.index}>
							{color.name}
						</option>
					{/each}
				</select>
				<div
					class="color-swatch"
					style="background-color: {COLOR_PALETTES.Skin[character.colorIndices?.Skin ?? 2]
						.hex}"
				/>
			</div>

			<div class="color-control">
				<label>Hair Color</label>
				<select
					value={character.colorIndices?.Hair ?? 3}
					on:change={(e) => updateColor('Hair', e.target.value)}
				>
					{#each COLOR_PALETTES.Hair as color}
						<option value={color.index}>
							{color.name}
						</option>
					{/each}
				</select>
				<div
					class="color-swatch"
					style="background-color: {COLOR_PALETTES.Hair[character.colorIndices?.Hair ?? 3]
						.hex}"
				/>
			</div>

			<div class="color-control">
				<label>Eye Color</label>
				<select
					value={character.colorIndices?.Eye ?? 2}
					on:change={(e) => updateColor('Eye', e.target.value)}
				>
					{#each COLOR_PALETTES.Eye as color}
						<option value={color.index}>
							{color.name}
						</option>
					{/each}
				</select>
				<div
					class="color-swatch"
					style="background-color: {COLOR_PALETTES.Eye[character.colorIndices?.Eye ?? 2].hex}"
				/>
			</div>

			<div class="color-control">
				<label>Accessory Color</label>
				<select
					value={character.colorIndices?.Accessory ?? 1}
					on:change={(e) => updateColor('Accessory', e.target.value)}
				>
					{#each COLOR_PALETTES.Accessory as color}
						<option value={color.index}>
							{color.name}
						</option>
					{/each}
				</select>
				<div
					class="color-swatch"
					style="background-color: {COLOR_PALETTES.Accessory[
						character.colorIndices?.Accessory ?? 1
					].hex}"
				/>
			</div>
		</div>
	</div>

	<!-- Layer Controls by Category -->
	<div class="categories">
		{#each sortedCategories as [categoryName, layers]}
			<div class="category">
				<h3>{categoryName}</h3>
				{#each layers as layer}
					{@const hairIndex = character.parts?.Hair?.index}
				{@const baseIndices = getAvailableIndices(layer.name, character.gender)}
				{@const indices = layer.name === 'HairBack' && hairIndex !== -1 ? getMatchingHairBackIndices(hairIndex, character.gender) : baseIndices}
					{@const partData = character.parts?.[layer.name] || { index: -1, variant: -1 }}
					{@const variants = partData.index !== -1 ? getAvailableVariants(layer.name, partData.index, character.gender) : []}
					{@const hasMoustache = character.parts?.Moustache?.index !== -1}
					{@const isMouthDisabled = layer.name === 'Mouth' && hasMoustache}
					{@const isFemaleHiddenLayer = character.gender === 'Female' && (layer.name === 'Beard' || layer.name === 'Moustache')}

					{#if indices.length > 0 && !isFemaleHiddenLayer}
						<div class="layer-control" class:disabled={isMouthDisabled}>
							<label>
								{layer.name.replace(/([A-Z])/g, ' $1').trim()}
								{#if isMouthDisabled}
									<span class="disabled-hint">(disabled when moustache present)</span>
								{/if}
							</label>
							<div class="part-selectors">
								<!-- Index selector -->
								<select
									class="index-select"
									value={partData.index}
									disabled={isMouthDisabled}
									on:change={(e) => {
										const newIndex = parseInt(e.target.value);
										if (newIndex === -1) {
											removePart(layer.name);
										} else {
											const availVariants = getAvailableVariants(layer.name, newIndex, character.gender);
											updatePart(layer.name, newIndex, availVariants[0] || 0);
										}
									}}
								>
									{#if layer.canBeNone}
										<option value="-1">None</option>
									{/if}
									{#each indices as index, i}
										{@const firstVariant = getAvailableVariants(layer.name, index, character.gender)[0] || 0}
										<option value={index}>{getSpriteLabel(layer.name, index, firstVariant)}</option>
									{/each}
								</select>

								<!-- Variant selector (only show if index is selected AND has multiple variants) -->
								{#if partData.index !== -1 && variants.length > 1}
									<select
										class="variant-select"
										value={partData.variant}
										disabled={isMouthDisabled}
										on:change={(e) => updatePart(layer.name, partData.index, e.target.value)}
									>
										{#each variants as variant, i}
											<option value={variant}>{getSpriteLabel(layer.name, partData.index, variant)}</option>
										{/each}
									</select>
								{/if}

								<!-- Remove button -->
								{#if layer.canBeNone && partData.index !== -1 && !isMouthDisabled}
									<button class="clear-btn" on:click={() => removePart(layer.name)} title="Remove">
										✕
									</button>
								{/if}
							</div>
						</div>
					{/if}
				{/each}
			</div>
		{/each}
	</div>
</div>

<style>
	.controls-container {
		background: white;
		border: 2px solid #333;
		border-radius: 8px;
		padding: 20px;
		max-height: 80vh;
		overflow-y: auto;
	}

	.controls-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
		padding-bottom: 10px;
		border-bottom: 1px solid #eee;
	}

	.controls-header h2 {
		margin: 0;
		color: #333;
	}

	.randomize-btn {
		background: #4caf50;
		color: white;
		border: none;
		padding: 10px 20px;
		border-radius: 5px;
		cursor: pointer;
		font-size: 16px;
		font-weight: bold;
	}

	.randomize-btn:hover {
		background: #45a049;
	}

	.section {
		margin-bottom: 20px;
		padding: 15px;
		background: #fafafa;
		border: 1px solid #ddd;
		border-radius: 5px;
	}

	.section h3 {
		margin: 0 0 10px 0;
		color: #555;
		font-size: 18px;
	}

	.section select {
		width: 100%;
		padding: 8px;
		border: 1px solid #ccc;
		border-radius: 3px;
		font-size: 14px;
	}

	.color-controls {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.color-control {
		display: grid;
		grid-template-columns: 100px 1fr 30px;
		align-items: center;
		gap: 10px;
	}

	.color-control label {
		font-weight: bold;
		color: #333;
		font-size: 14px;
	}

	.color-swatch {
		width: 30px;
		height: 30px;
		border: 2px solid #333;
		border-radius: 4px;
	}

	.categories {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.category {
		border: 1px solid #ddd;
		border-radius: 5px;
		padding: 15px;
		background: #fafafa;
	}

	.category h3 {
		margin: 0 0 15px 0;
		color: #555;
		font-size: 18px;
		border-bottom: 1px solid #ddd;
		padding-bottom: 5px;
	}

	.layer-control {
		margin-bottom: 15px;
	}

	.layer-control:last-child {
		margin-bottom: 0;
	}

	.layer-control.disabled {
		opacity: 0.5;
	}

	.layer-control label {
		display: block;
		margin-bottom: 5px;
		font-weight: bold;
		color: #333;
		font-size: 14px;
	}

	.disabled-hint {
		font-weight: normal;
		font-size: 12px;
		color: #999;
		font-style: italic;
	}

	.part-selectors {
		display: flex;
		gap: 5px;
		align-items: center;
	}

	.index-select {
		flex: 2;
		padding: 8px;
		border: 1px solid #ccc;
		border-radius: 3px;
		background: white;
		font-size: 14px;
	}

	.variant-select {
		flex: 1;
		padding: 8px;
		border: 1px solid #ccc;
		border-radius: 3px;
		background: white;
		font-size: 14px;
	}

	.clear-btn {
		background: #f44336;
		color: white;
		border: none;
		width: 30px;
		height: 30px;
		border-radius: 50%;
		cursor: pointer;
		font-size: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.clear-btn:hover {
		background: #d32f2f;
	}
</style>
