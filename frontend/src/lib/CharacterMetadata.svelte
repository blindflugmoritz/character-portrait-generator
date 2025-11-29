<script>
	export let metadata = {};

	// Initialize metadata if empty
	if (!metadata.Id) {
		// Generate UUID with fallback for SSR
		let id;
		try {
			id = crypto.randomUUID();
		} catch (e) {
			id = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
		}

		metadata = {
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

	const genders = ['Male', 'Female'];
	const classes = ['AirCrew', 'BaseCrew'];
	const jobs = ['None', 'AAFCook', 'FieldMechanic', 'FieldEngineer', 'RAFMedic', 'AAFLabour'];
	const roles = ['None', 'Pilot', 'Gunner', 'Navigator', 'BombAimer', 'FlightEngineer', 'RadioOperator'];

	function updateField(field, value) {
		metadata = { ...metadata, [field]: value };
	}

	function updateBiography(value) {
		metadata = { ...metadata, Biography: { ...metadata.Biography, en: value } };
	}

	function updateSkillRank(skill, value) {
		const rank = Math.max(0, Math.min(6, parseInt(value) || 0));
		metadata = {
			...metadata,
			SkillRanks: { ...metadata.SkillRanks, [skill]: rank }
		};
	}

	// Handle class change - reset Job or Role accordingly
	function handleClassChange(newClass) {
		if (newClass === 'BaseCrew') {
			metadata = { ...metadata, Class: newClass, Role: 'None' };
		} else {
			metadata = { ...metadata, Class: newClass, Job: 'None' };
		}
	}
</script>

<div class="metadata-container">
	<h2>Character Information</h2>

	<div class="form-section">
		<h3>Basic Info</h3>

		<div class="form-row">
			<label for="creatorName">Creator Name</label>
			<input
				id="creatorName"
				type="text"
				value={metadata.CreatorName}
				on:input={(e) => updateField('CreatorName', e.target.value)}
				placeholder="Your name"
			/>
		</div>

		<div class="form-row">
			<label for="firstName">First Name</label>
			<input
				id="firstName"
				type="text"
				value={metadata.FirstName}
				on:input={(e) => updateField('FirstName', e.target.value)}
				placeholder="Character's first name"
			/>
		</div>

		<div class="form-row">
			<label for="lastName">Last Name</label>
			<input
				id="lastName"
				type="text"
				value={metadata.LastName}
				on:input={(e) => updateField('LastName', e.target.value)}
				placeholder="Character's last name"
			/>
		</div>

		{#if metadata.Class === 'AirCrew'}
			<div class="form-row">
				<label for="nickname">Nickname</label>
				<input
					id="nickname"
					type="text"
					value={metadata.Nickname}
					on:input={(e) => updateField('Nickname', e.target.value)}
					placeholder="e.g., Chief, Ace, etc."
				/>
			</div>
		{/if}

		<div class="form-row">
			<label for="birthDate">Birth Date</label>
			<input
				id="birthDate"
				type="date"
				value={metadata.BirthDate}
				max="1921-12-31"
				on:input={(e) => updateField('BirthDate', e.target.value)}
			/>
			<small>Must be before 1922</small>
		</div>

		<div class="form-row">
			<label for="gender">Gender</label>
			<select id="gender" value={metadata.Gender} on:change={(e) => updateField('Gender', e.target.value)}>
				{#each genders as gender}
					<option value={gender}>{gender}</option>
				{/each}
			</select>
		</div>
	</div>

	<div class="form-section">
		<h3>Role & Class</h3>

		<div class="form-row">
			<label for="class">Class</label>
			<select id="class" value={metadata.Class} on:change={(e) => handleClassChange(e.target.value)}>
				{#each classes as cls}
					<option value={cls}>{cls}</option>
				{/each}
			</select>
		</div>

		{#if metadata.Class === 'BaseCrew'}
			<div class="form-row">
				<label for="job">Job</label>
				<select id="job" value={metadata.Job} on:change={(e) => updateField('Job', e.target.value)}>
					{#each jobs as job}
						<option value={job}>{job.replace(/([A-Z])/g, ' $1').trim()}</option>
					{/each}
				</select>
			</div>
		{:else}
			<div class="form-row">
				<label for="role">Role</label>
				<select id="role" value={metadata.Role} on:change={(e) => updateField('Role', e.target.value)}>
					{#each roles as role}
						<option value={role}>{role.replace(/([A-Z])/g, ' $1').trim()}</option>
					{/each}
				</select>
			</div>
		{/if}
	</div>

	<div class="form-section">
		<h3>Biography</h3>
		<textarea
			value={metadata.Biography?.en || ''}
			on:input={(e) => updateBiography(e.target.value)}
			placeholder="Write the character's background story..."
			rows="4"
		/>
	</div>

	{#if metadata.Class === 'AirCrew'}
		<div class="form-section">
			<h3>Skill Ranks (0-6)</h3>
			<div class="skills-grid">
				{#each Object.entries(metadata.SkillRanks) as [skill, rank]}
					<div class="skill-control">
						<label for="skill-{skill}">{skill}</label>
						<div class="skill-input">
							<input
								id="skill-{skill}"
								type="number"
								min="0"
								max="6"
								value={rank}
								on:input={(e) => updateSkillRank(skill, e.target.value)}
							/>
							<input
								type="range"
								min="0"
								max="6"
								value={rank}
								on:input={(e) => updateSkillRank(skill, e.target.value)}
							/>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.metadata-container {
		background: white;
		border: 2px solid #333;
		border-radius: 8px;
		padding: 20px;
		max-height: 80vh;
		overflow-y: auto;
	}

	h2 {
		margin: 0 0 20px 0;
		color: #333;
		font-size: 24px;
		border-bottom: 2px solid #333;
		padding-bottom: 10px;
	}

	.form-section {
		margin-bottom: 25px;
		padding: 15px;
		background: #fafafa;
		border: 1px solid #ddd;
		border-radius: 5px;
	}

	.form-section h3 {
		margin: 0 0 15px 0;
		color: #555;
		font-size: 18px;
		border-bottom: 1px solid #ddd;
		padding-bottom: 5px;
	}

	.form-row {
		margin-bottom: 15px;
	}

	.form-row:last-child {
		margin-bottom: 0;
	}

	label {
		display: block;
		margin-bottom: 5px;
		font-weight: bold;
		color: #333;
		font-size: 14px;
	}

	input[type='text'],
	input[type='date'],
	select,
	textarea {
		width: 100%;
		padding: 8px;
		border: 1px solid #ccc;
		border-radius: 3px;
		font-size: 14px;
		font-family: inherit;
	}

	input[type='text']:focus,
	input[type='date']:focus,
	select:focus,
	textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
	}

	small {
		display: block;
		margin-top: 5px;
		color: #666;
		font-size: 12px;
	}

	textarea {
		resize: vertical;
		min-height: 80px;
	}

	.skills-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 15px;
	}

	.skill-control label {
		font-size: 13px;
	}

	.skill-input {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.skill-input input[type='number'] {
		width: 60px;
		text-align: center;
	}

	.skill-input input[type='range'] {
		flex: 1;
	}

	@media (max-width: 768px) {
		.skills-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
