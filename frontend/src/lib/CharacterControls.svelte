<script>
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import * as Select from '$lib/components/ui/select';
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

	let { character = $bindable(), onRandomize, onUpdate } = $props();

	// Local state for Select components
	let genderValue = $state(character.gender);
	let bodyShapeValue = $state(String(character.bodyShapeIndex));
	let skinColorValue = $state(String(character.colorIndices?.Skin ?? 2));
	let hairColorValue = $state(String(character.colorIndices?.Hair ?? 3));
	let eyeColorValue = $state(String(character.colorIndices?.Eye ?? 2));
	let accessoryColorValue = $state(String(character.colorIndices?.Accessory ?? 1));

	// Sync local state with character when it changes externally
	$effect(() => {
		genderValue = character.gender;
		bodyShapeValue = String(character.bodyShapeIndex);
		skinColorValue = String(character.colorIndices?.Skin ?? 2);
		hairColorValue = String(character.colorIndices?.Hair ?? 3);
		eyeColorValue = String(character.colorIndices?.Eye ?? 2);
		accessoryColorValue = String(character.colorIndices?.Accessory ?? 1);
	});

	// Watch local state and update character
	$effect(() => {
		if (genderValue !== character.gender) {
			updateGender(genderValue);
		}
	});

	$effect(() => {
		const newBodyShape = parseInt(bodyShapeValue);
		if (newBodyShape !== character.bodyShapeIndex) {
			updateBodyShape(bodyShapeValue);
		}
	});

	$effect(() => {
		const newSkin = parseInt(skinColorValue);
		if (newSkin !== (character.colorIndices?.Skin ?? 2)) {
			updateColor('Skin', skinColorValue);
		}
	});

	$effect(() => {
		const newHair = parseInt(hairColorValue);
		if (newHair !== (character.colorIndices?.Hair ?? 3)) {
			updateColor('Hair', hairColorValue);
		}
	});

	$effect(() => {
		const newEye = parseInt(eyeColorValue);
		if (newEye !== (character.colorIndices?.Eye ?? 2)) {
			updateColor('Eye', eyeColorValue);
		}
	});

	$effect(() => {
		const newAccessory = parseInt(accessoryColorValue);
		if (newAccessory !== (character.colorIndices?.Accessory ?? 1)) {
			updateColor('Accessory', accessoryColorValue);
		}
	});

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
		const newCharacter = generateRandomCharacter(character.gender);
		// Update properties in-place to maintain binding
		character.gender = newCharacter.gender;
		character.bodyShapeIndex = newCharacter.bodyShapeIndex;
		character.colorIndices = { ...newCharacter.colorIndices };
		character.parts = { ...newCharacter.parts };

		// Notify parent to update thumbnail immediately
		if (onRandomize) {
			onRandomize();
		}

		// Also notify parent to save changes (onRandomize handles this, but kept for clarity)
		// Note: onRandomize already calls forceUpdateThumbnail which saves to crew array
	}

	// Update gender - regenerate random character with new gender
	function updateGender(newGender) {
		const newCharacter = generateRandomCharacter(newGender);

		// Update properties in-place to maintain binding
		character.gender = newCharacter.gender;
		character.bodyShapeIndex = newCharacter.bodyShapeIndex;
		character.colorIndices = { ...newCharacter.colorIndices };
		character.parts = { ...newCharacter.parts };

		// Notify parent to save changes
		if (onUpdate) onUpdate();
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

		// Notify parent to save changes
		if (onUpdate) onUpdate();
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

		// Notify parent to save changes
		if (onUpdate) onUpdate();
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

		// Notify parent to save changes
		if (onUpdate) onUpdate();
	}

	// Update body shape
	function updateBodyShape(shapeIndex) {
		character = {
			...character,
			bodyShapeIndex: parseInt(shapeIndex)
		};

		// Notify parent to save changes
		if (onUpdate) onUpdate();
	}

	// Get layers grouped by category
	let layersByCategory = $derived(
		Object.entries(LAYERS).reduce((acc, [name, layer]) => {
			if (!acc[layer.category]) {
				acc[layer.category] = [];
			}
			acc[layer.category].push({ name, ...layer });
			return acc;
		}, {})
	);

	// Sort categories with Background at the end
	let sortedCategories = $derived(
		Object.entries(layersByCategory).sort(([catA], [catB]) => {
			if (catA === 'Background') return 1;
			if (catB === 'Background') return -1;
			return 0;
		})
	);

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

<div class="bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm p-6">
	<div class="flex justify-between items-center mb-6">
		<h2 class="text-2xl font-bold">Character Customization</h2>
		<Button onclick={randomizeCharacter} variant="default">
			🎲 Randomize
		</Button>
	</div>

	<!-- Gender Selection -->
	<div class="mb-6">
		<Label>Gender</Label>
		<Select.Root type="single" bind:value={genderValue}>
			<Select.Trigger class="w-full">
				{genderValue}
			</Select.Trigger>
			<Select.Content>
				<Select.Item value="Male">Male</Select.Item>
				<Select.Item value="Female">Female</Select.Item>
			</Select.Content>
		</Select.Root>
	</div>

	<!-- Body Shape Selection -->
	<div class="mb-6">
		<Label>Body Shape</Label>
		<Select.Root type="single" bind:value={bodyShapeValue}>
			<Select.Trigger class="w-full">
				{BODY_SHAPES.find(s => String(s.index) === bodyShapeValue)?.name || 'Average'}
			</Select.Trigger>
			<Select.Content>
				{#each BODY_SHAPES as shape}
					<Select.Item value={String(shape.index)}>{shape.name}</Select.Item>
				{/each}
			</Select.Content>
		</Select.Root>
	</div>

	<!-- Color Selection -->
	<div class="mb-6">
		<Label class="text-lg font-semibold mb-3 block">Colors</Label>
		<div class="space-y-4">
			<!-- Skin Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Skin Color</Label>
				<Select.Root type="single" bind:value={skinColorValue}>
					<Select.Trigger class="flex-1">
						{COLOR_PALETTES.Skin.find(c => String(c.index) === skinColorValue)?.name || 'Unknown'}
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Skin as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Skin[parseInt(skinColorValue)].hex}"
				></div>
			</div>

			<!-- Hair Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Hair Color</Label>
				<Select.Root type="single" bind:value={hairColorValue}>
					<Select.Trigger class="flex-1">
						{COLOR_PALETTES.Hair.find(c => String(c.index) === hairColorValue)?.name || 'Unknown'}
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Hair as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Hair[parseInt(hairColorValue)].hex}"
				></div>
			</div>

			<!-- Eye Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Eye Color</Label>
				<Select.Root type="single" bind:value={eyeColorValue}>
					<Select.Trigger class="flex-1">
						{COLOR_PALETTES.Eye.find(c => String(c.index) === eyeColorValue)?.name || 'Unknown'}
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Eye as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Eye[parseInt(eyeColorValue)].hex}"
				></div>
			</div>

			<!-- Accessory Color -->
			<div class="flex items-center gap-3">
				<Label class="w-32">Accessory Color</Label>
				<Select.Root type="single" bind:value={accessoryColorValue}>
					<Select.Trigger class="flex-1">
						{COLOR_PALETTES.Accessory.find(c => String(c.index) === accessoryColorValue)?.name || 'Unknown'}
					</Select.Trigger>
					<Select.Content>
						{#each COLOR_PALETTES.Accessory as color}
							<Select.Item value={String(color.index)}>{color.name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
				<div
					class="w-8 h-8 rounded border-2 border-gray-300"
					style="background-color: {COLOR_PALETTES.Accessory[parseInt(accessoryColorValue)].hex}"
				></div>
			</div>
		</div>
	</div>

	<!-- Layer Controls by Category -->
	<div class="space-y-6">
		{#each sortedCategories as [categoryName, layers]}
			{@const hairIndex = character.parts?.Hair?.index}
			<div class="border rounded-lg p-4 bg-muted/50">
				<h3 class="text-lg font-semibold mb-4">{categoryName}</h3>
				<div class="space-y-4">
					{#each layers as layer}
						{@const baseIndices = getAvailableIndices(layer.name, character.gender)}
						{@const indices = layer.name === 'HairBack' && hairIndex !== -1 ? getMatchingHairBackIndices(hairIndex, character.gender) : baseIndices}
						{@const partData = character.parts?.[layer.name] || { index: -1, variant: -1 }}
						{@const variants = partData.index !== -1 ? getAvailableVariants(layer.name, partData.index, character.gender) : []}
						{@const hasMoustache = character.parts?.Moustache?.index !== -1}
						{@const isMouthDisabled = layer.name === 'Mouth' && hasMoustache}
						{@const isFemaleHiddenLayer = character.gender === 'Female' && (layer.name === 'Beard' || layer.name === 'Moustache')}

						{#if indices.length > 0 && !isFemaleHiddenLayer}
							{@const indexLabel = partData.index === -1 ? 'None' : getSpriteLabel(layer.name, partData.index, getAvailableVariants(layer.name, partData.index, character.gender)[0] || 0)}
							<div class:opacity-50={isMouthDisabled}>
								<Label>
									{layer.name.replace(/([A-Z])/g, ' $1').trim()}
									{#if isMouthDisabled}
										<span class="text-xs text-muted-foreground">(disabled when moustache present)</span>
									{/if}
								</Label>
								<div class="flex gap-2 mt-2">
									<!-- Index selector -->
									<select
										class="flex h-10 flex-[2] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
										value={partData.index}
										onchange={(e) => {
											if (isMouthDisabled) return;
											const newIndex = parseInt(e.target.value);
											if (newIndex === -1) {
												removePart(layer.name);
											} else {
												const availVariants = getAvailableVariants(layer.name, newIndex, character.gender);
												updatePart(layer.name, newIndex, availVariants[0] || 0);
											}
										}}
										disabled={isMouthDisabled}
									>
										{#if layer.canBeNone}
											<option value="-1">None</option>
										{/if}
										{#each indices as index}
											{@const firstVariant = getAvailableVariants(layer.name, index, character.gender)[0] || 0}
											{@const label = getSpriteLabel(layer.name, index, firstVariant)}
											<option value={index}>{label}</option>
										{/each}
									</select>

									<!-- Variant selector (only show if index is selected AND has multiple variants) -->
									{#if partData.index !== -1 && variants.length > 1}
										{@const variantLabel = getSpriteLabel(layer.name, partData.index, partData.variant)}
										<select
											class="flex h-10 flex-1 items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
											value={partData.variant}
											onchange={(e) => {
												if (!isMouthDisabled) {
													updatePart(layer.name, partData.index, e.target.value);
												}
											}}
											disabled={isMouthDisabled}
										>
											{#each variants as variant}
												{@const label = getSpriteLabel(layer.name, partData.index, variant)}
												<option value={variant}>{label}</option>
											{/each}
										</select>
									{/if}

									<!-- Remove button -->
									{#if layer.canBeNone && partData.index !== -1 && !isMouthDisabled}
										<Button onclick={() => removePart(layer.name)} variant="destructive" size="icon">
											✕
										</Button>
									{/if}
								</div>
							</div>
						{/if}
					{/each}
				</div>
			</div>
		{/each}
	</div>
</div>
