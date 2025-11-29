<script>
	import { onMount } from 'svelte';
	import PortraitCanvas from '$lib/PortraitCanvas.svelte';
	import CharacterControls from '$lib/CharacterControls.svelte';
	import CharacterMetadata from '$lib/CharacterMetadata.svelte';
	import CrewList from '$lib/CrewList.svelte';
	import CrewGenerator from '$lib/CrewGenerator.svelte';
	import PhotoUpload from '$lib/PhotoUpload.svelte';
	import { createDefaultCharacter, generateRandomCharacter } from '$lib/assetData.js';

	// Crew management
	let crew = [];
	let selectedCrewIndex = 0;

	// Current crew member being edited
	let character = createDefaultCharacter();
	let metadata = createDefaultMetadata();

	let portraitCanvas;
	let activeTab = 'appearance';

	// Initialize crew array
	crew = [createCrewMember()];
	character = crew[0].character;
	metadata = crew[0].metadata;

	// Initialize with one crew member
	onMount(() => {
		// Check for data version - clear if old version
		const DATA_VERSION = '2.0'; // Increment this when data structure changes
		const savedVersion = localStorage.getItem('crewDataVersion');

		if (savedVersion !== DATA_VERSION) {
			console.log('Data version mismatch, clearing localStorage');
			localStorage.removeItem('crew');
			localStorage.setItem('crewDataVersion', DATA_VERSION);
			return;
		}

		// Try to load from localStorage
		try {
			const saved = localStorage.getItem('crew');
			if (saved) {
				const parsed = JSON.parse(saved);
				if (parsed && Array.isArray(parsed) && parsed.length > 0) {
					crew = parsed;
					character = crew[selectedCrewIndex].character;
					metadata = crew[selectedCrewIndex].metadata;
				}
			}
		} catch (e) {
			console.error('Failed to load crew from localStorage:', e);
		}
	});

	// Save to localStorage whenever crew changes (browser only)
	function saveCrew() {
		if (typeof window !== 'undefined' && crew.length > 0) {
			try {
				localStorage.setItem('crew', JSON.stringify(crew));
			} catch (e) {
				console.error('Failed to save crew to localStorage:', e);
			}
		}
	}

	// Update crew member when character or metadata changes
	$: if (crew[selectedCrewIndex]) {
		crew[selectedCrewIndex].character = character;
		crew[selectedCrewIndex].metadata = metadata;
		saveCrew();
	}

	function createDefaultMetadata() {
		// Generate UUID with fallback for SSR
		let id;
		try {
			id = crypto.randomUUID();
		} catch (e) {
			// Fallback for SSR: simple random ID
			id = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
		}

		return {
			Id: id,
			CreatorName: '',
			FirstName: '',
			LastName: '',
			Nickname: '',
			BirthDate: '1920-01-01',
			Gender: 'Male',
			Class: 'AirCrew',
			Job: 'None',
			Role: 'Pilot',
			Biography: { en: '' },
			SkillRanks: {
				Flying: 0,
				Shooting: 0,
				Bombing: 0,
				Endurance: 0,
				Engineering: 0,
				Navigating: 0
			}
		};
	}

	function createCrewMember() {
		return {
			character: createDefaultCharacter(),
			metadata: createDefaultMetadata()
		};
	}

	// Crew management functions
	function addCrewMember() {
		const newMember = createCrewMember();
		crew = [...crew, newMember];
		selectedCrewIndex = crew.length - 1;
		character = newMember.character;
		metadata = newMember.metadata;
	}

	function deleteCrewMember(index) {
		if (crew.length <= 1) {
			alert('You must have at least one crew member!');
			return;
		}

		crew = crew.filter((_, i) => i !== index);

		// Adjust selected index if needed
		if (selectedCrewIndex >= crew.length) {
			selectedCrewIndex = crew.length - 1;
		}

		// Load the character and metadata of the newly selected member
		character = crew[selectedCrewIndex].character;
		metadata = crew[selectedCrewIndex].metadata;
	}

	function selectCrewMember(index) {
		selectedCrewIndex = index;
		character = crew[index].character;
		metadata = crew[index].metadata;
	}

	// Handle AI-generated crew
	function handleCrewGenerated(generatedCrew, replaceExisting) {
		if (replaceExisting) {
			crew = generatedCrew;
			selectedCrewIndex = 0;
		} else {
			crew = [...crew, ...generatedCrew];
			// Don't change selection when adding to existing crew
		}

		// Load the selected crew member
		if (crew.length > 0) {
			character = crew[selectedCrewIndex].character;
			metadata = crew[selectedCrewIndex].metadata;
		}
	}

	// Handle photo-generated character
	function handlePhotoAnalyzed(generatedCharacter) {
		// Update current crew member's character
		character = generatedCharacter;
		crew[selectedCrewIndex].character = generatedCharacter;
	}

	// Export portrait as PNG
	function exportPortrait() {
		if (portraitCanvas) {
			const dataUrl = portraitCanvas.exportPortrait();
			const link = document.createElement('a');
			const fileName =
				metadata.FirstName && metadata.LastName
					? `${metadata.FirstName}_${metadata.LastName}.png`
					: 'character-portrait.png';
			link.download = fileName;
			link.href = dataUrl;
			link.click();
		}
	}

	// Export single character data as JSON
	function exportJSON() {
		const editorData = {
			BodyShapeIndex: character.bodyShapeIndex || 1,
			AccessoryColorIndex: character.colorIndices?.Accessory ?? 1,
			SkinColorIndex: character.colorIndices?.Skin ?? 2,
			HairColorIndex: character.colorIndices?.Hair ?? 3,
			EyeColorIndex: character.colorIndices?.Eye ?? 2
		};

		const partMapping = {
			AccessoryFront: 'Accessory',
			Blemish: 'Blemish',
			Nose: 'Nose',
			Eyebrows: 'Eyebrows',
			Eyes: 'Eyes',
			Moustache: 'Moustache',
			Beard: 'Beard',
			Mouth: 'Mouth',
			Hair: 'Hair',
			DetailUpper: 'Detail',
			Headshape: 'Headshape',
			Ears: 'Ears'
		};

		for (const [layerName, jsonKey] of Object.entries(partMapping)) {
			const part = character.parts[layerName] || { index: -1, variant: -1 };
			editorData[jsonKey] = {
				Index: part.index,
				Variant: part.variant
			};
		}

		const exportData = {
			...metadata,
			EditorData: editorData
		};

		const jsonStr = JSON.stringify(exportData, null, 2);
		const blob = new Blob([jsonStr], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		const fileName =
			metadata.FirstName && metadata.LastName
				? `${metadata.FirstName}_${metadata.LastName}.json`
				: 'character-data.json';
		link.download = fileName;
		link.href = url;
		link.click();
		URL.revokeObjectURL(url);
	}

	// Export entire crew as JSON array
	function exportCrewJSON() {
		const crewData = crew.map((member) => {
			const editorData = {
				BodyShapeIndex: member.character.bodyShapeIndex || 1,
				AccessoryColorIndex: member.character.colorIndices?.Accessory ?? 1,
				SkinColorIndex: member.character.colorIndices?.Skin ?? 2,
				HairColorIndex: member.character.colorIndices?.Hair ?? 3,
				EyeColorIndex: member.character.colorIndices?.Eye ?? 2
			};

			const partMapping = {
				AccessoryFront: 'Accessory',
				Blemish: 'Blemish',
				Nose: 'Nose',
				Eyebrows: 'Eyebrows',
				Eyes: 'Eyes',
				Moustache: 'Moustache',
				Beard: 'Beard',
				Mouth: 'Mouth',
				Hair: 'Hair',
				DetailUpper: 'Detail',
				Headshape: 'Headshape',
				Ears: 'Ears'
			};

			for (const [layerName, jsonKey] of Object.entries(partMapping)) {
				const part = member.character.parts[layerName] || { index: -1, variant: -1 };
				editorData[jsonKey] = {
					Index: part.index,
					Variant: part.variant
				};
			}

			return {
				...member.metadata,
				EditorData: editorData
			};
		});

		const jsonStr = JSON.stringify(crewData, null, 2);
		const blob = new Blob([jsonStr], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.download = 'crew-data.json';
		link.href = url;
		link.click();
		URL.revokeObjectURL(url);
	}

	// Import crew from JSON
	function importCrewJSON() {
		const input = document.createElement('input');
		input.type = 'file';
		input.accept = '.json';
		input.onchange = (e) => {
			const file = e.target.files[0];
			if (file) {
				const reader = new FileReader();
				reader.onload = (event) => {
					try {
						const importedData = JSON.parse(event.target.result);

						// Check if it's an array (crew) or single character
						const dataArray = Array.isArray(importedData) ? importedData : [importedData];

						// Convert imported data to internal format
						const importedCrew = dataArray.map((charData) => {
							const editorData = charData.EditorData || {};

							const character = {
								bodyShapeIndex: editorData.BodyShapeIndex ?? 1,
								colorIndices: {
									Skin: editorData.SkinColorIndex ?? 2,
									Hair: editorData.HairColorIndex ?? 3,
									Eye: editorData.EyeColorIndex ?? 2,
									Accessory: editorData.AccessoryColorIndex ?? 1
								},
								parts: {
									AccessoryFront: editorData.Accessory || { index: -1, variant: -1 },
									Blemish: editorData.Blemish || { index: -1, variant: -1 },
									Nose: editorData.Nose || { index: 0, variant: 0 },
									Eyebrows: editorData.Eyebrows || { index: 0, variant: 0 },
									Eyes: editorData.Eyes || { index: 0, variant: 0 },
									Moustache: editorData.Moustache || { index: -1, variant: -1 },
									Beard: editorData.Beard || { index: -1, variant: -1 },
									Mouth: editorData.Mouth || { index: 0, variant: 0 },
									Hair: editorData.Hair || { index: 0, variant: 0 },
									HairBack: { index: 4, variant: 0 },
									DetailUpper: editorData.Detail || { index: -1, variant: -1 },
									DetailLower: { index: -1, variant: -1 },
									Headshape: editorData.Headshape || { index: 0, variant: 0 },
									HeadAuxiliary: { index: -1, variant: -1 },
									Ears: editorData.Ears || { index: 0, variant: 0 },
									Body: { index: 0, variant: 0 },
									Clothes: { index: 0, variant: 0 },
									ClothesBack: { index: 0, variant: 0 }
								}
							};

							// Generate UUID with fallback
							let id = charData.Id;
							if (!id) {
								try {
									id = crypto.randomUUID();
								} catch (e) {
									id = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
								}
							}

							const metadata = {
								Id: id,
								CreatorName: charData.CreatorName || '',
								FirstName: charData.FirstName || '',
								LastName: charData.LastName || '',
								Nickname: charData.Nickname || '',
								BirthDate: charData.BirthDate || '1920-01-01',
								Gender: charData.Gender || 'Male',
								Class: charData.Class || 'AirCrew',
								Job: charData.Job || 'None',
								Role: charData.Role || 'Pilot',
								Biography: charData.Biography || { en: '' },
								SkillRanks: charData.SkillRanks || {
									Flying: 0,
									Shooting: 0,
									Bombing: 0,
									Endurance: 0,
									Engineering: 0,
									Navigating: 0
								}
							};

							return { character, metadata };
						});

						crew = importedCrew;
						selectedCrewIndex = 0;
						alert(`Successfully imported ${importedCrew.length} crew member(s)!`);
					} catch (err) {
						alert('Failed to import crew data. Invalid JSON format.');
						console.error(err);
					}
				};
				reader.readAsText(file);
			}
		};
		input.click();
	}

	// Share portrait
	function sharePortrait() {
		if (portraitCanvas && navigator.share) {
			const dataUrl = portraitCanvas.exportPortrait();
			fetch(dataUrl)
				.then((res) => res.blob())
				.then((blob) => {
					const file = new File([blob], 'character-portrait.png', { type: 'image/png' });
					navigator.share({
						title: 'My Character Portrait',
						text: `Check out ${metadata.FirstName || 'my'} ${metadata.LastName || 'character'}!`,
						files: [file]
					});
				});
		} else if (navigator.clipboard && portraitCanvas) {
			const dataUrl = portraitCanvas.exportPortrait();
			fetch(dataUrl)
				.then((res) => res.blob())
				.then((blob) => {
					navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
					alert('Portrait copied to clipboard!');
				});
		}
	}
</script>

<svelte:head>
	<title>Crew Portrait Generator</title>
	<meta name="description" content="Create custom character portraits for your crew" />
</svelte:head>

<main>
	<header>
		<h1>Crew Portrait Generator</h1>
		<p>Create and manage your entire crew with customizable portraits and metadata</p>
	</header>

	<div class="main-container">
		<!-- AI Crew Generator -->
		<CrewGenerator onCrewGenerated={handleCrewGenerated} />

		<!-- Photo Upload -->
		<PhotoUpload onPhotoAnalyzed={handlePhotoAnalyzed} />

		<!-- Crew List Section -->
		<CrewList
			{crew}
			selectedIndex={selectedCrewIndex}
			onSelect={selectCrewMember}
			onDelete={deleteCrewMember}
			onAdd={addCrewMember}
		/>

		<div class="generator-container">
			<div class="portrait-section">
				<h3 class="current-member-title">
					Editing: {metadata.FirstName || 'Unnamed'} {metadata.LastName || ''}
				</h3>
				<PortraitCanvas bind:this={portraitCanvas} {character} canvasSize={512} />

				<div class="portrait-actions">
					<button class="export-btn" on:click={exportPortrait}> 💾 Download PNG </button>
					<button class="json-btn" on:click={exportJSON}> 📄 Export Character </button>
					<button class="share-btn" on:click={sharePortrait}> 📤 Share </button>
				</div>

				<div class="crew-actions">
					<button class="crew-export-btn" on:click={exportCrewJSON}> 📦 Export Crew </button>
					<button class="crew-import-btn" on:click={importCrewJSON}> 📥 Import Crew </button>
				</div>
			</div>

			<div class="controls-section">
				<div class="tabs">
					<button
						class="tab"
						class:active={activeTab === 'appearance'}
						on:click={() => (activeTab = 'appearance')}
					>
						Appearance
					</button>
					<button
						class="tab"
						class:active={activeTab === 'info'}
						on:click={() => (activeTab = 'info')}
					>
						Character Info
					</button>
				</div>

				{#if activeTab === 'appearance'}
					<CharacterControls bind:character />
				{:else}
					<CharacterMetadata bind:metadata />
				{/if}
			</div>
		</div>
	</div>

	<footer>
		<p>Built with SvelteKit • {crew.length} crew member(s) • Advanced color system</p>
	</footer>
</main>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		min-height: 100vh;
	}

	main {
		padding: 20px;
		max-width: 1600px;
		margin: 0 auto;
	}

	header {
		text-align: center;
		margin-bottom: 30px;
		color: white;
	}

	header h1 {
		font-size: 3em;
		margin: 0 0 10px 0;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
	}

	header p {
		font-size: 1.2em;
		margin: 0;
		opacity: 0.9;
	}

	.main-container {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.generator-container {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 30px;
		align-items: start;
	}

	.portrait-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 15px;
	}

	.current-member-title {
		color: white;
		font-size: 20px;
		margin: 0;
		padding: 10px 20px;
		background: rgba(0, 0, 0, 0.3);
		border-radius: 8px;
		text-align: center;
	}

	.portrait-actions,
	.crew-actions {
		display: flex;
		gap: 10px;
		flex-wrap: wrap;
		justify-content: center;
	}

	.export-btn,
	.json-btn,
	.share-btn,
	.crew-export-btn,
	.crew-import-btn {
		padding: 12px 24px;
		border: none;
		border-radius: 6px;
		font-size: 16px;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.export-btn {
		background: #2196f3;
		color: white;
	}

	.export-btn:hover {
		background: #1976d2;
		transform: translateY(-2px);
	}

	.json-btn {
		background: #4caf50;
		color: white;
	}

	.json-btn:hover {
		background: #45a049;
		transform: translateY(-2px);
	}

	.share-btn {
		background: #ff9800;
		color: white;
	}

	.share-btn:hover {
		background: #f57c00;
		transform: translateY(-2px);
	}

	.crew-export-btn {
		background: #9c27b0;
		color: white;
	}

	.crew-export-btn:hover {
		background: #7b1fa2;
		transform: translateY(-2px);
	}

	.crew-import-btn {
		background: #00bcd4;
		color: white;
	}

	.crew-import-btn:hover {
		background: #0097a7;
		transform: translateY(-2px);
	}

	.controls-section {
		min-width: 500px;
		max-width: 600px;
	}

	.tabs {
		display: flex;
		gap: 5px;
		margin-bottom: 10px;
	}

	.tab {
		flex: 1;
		padding: 12px 20px;
		background: white;
		border: 2px solid #333;
		border-bottom: none;
		border-radius: 8px 8px 0 0;
		font-size: 16px;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.2s ease;
		color: #666;
	}

	.tab:hover {
		background: #f5f5f5;
	}

	.tab.active {
		background: white;
		color: #333;
		border-bottom: 2px solid white;
		position: relative;
		z-index: 1;
	}

	footer {
		text-align: center;
		margin-top: 40px;
		color: white;
		opacity: 0.8;
	}

	@media (max-width: 1200px) {
		.generator-container {
			grid-template-columns: 1fr;
			gap: 20px;
		}

		.controls-section {
			min-width: auto;
			max-width: none;
		}

		header h1 {
			font-size: 2.5em;
		}
	}

	@media (max-width: 768px) {
		main {
			padding: 15px;
		}

		header h1 {
			font-size: 2em;
		}

		header p {
			font-size: 1em;
		}

		.portrait-actions,
		.crew-actions {
			flex-direction: column;
			width: 100%;
		}

		.export-btn,
		.json-btn,
		.share-btn,
		.crew-export-btn,
		.crew-import-btn {
			width: 100%;
		}

		.tabs {
			flex-direction: column;
		}

		.tab {
			border-radius: 8px;
			border: 2px solid #333;
		}

		.tab.active {
			border: 2px solid #333;
		}
	}
</style>
