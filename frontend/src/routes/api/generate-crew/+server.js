import { json } from '@sveltejs/kit';
import Anthropic from '@anthropic-ai/sdk';
import { ANTHROPIC_API_KEY } from '$env/static/private';
import { generateRandomCharacter } from '$lib/assetData.js';

const anthropic = new Anthropic({
	apiKey: ANTHROPIC_API_KEY
});

export async function POST({ request }) {
	try {
		const { description, replaceExisting = false } = await request.json();

		if (!description || description.trim().length === 0) {
			return json({ error: 'Description is required' }, { status: 400 });
		}

		console.log('Starting crew generation for description:', description);
		console.log('API Key exists:', !!ANTHROPIC_API_KEY);
		console.log('API Key prefix:', ANTHROPIC_API_KEY?.substring(0, 20));

		// Call Claude API with structured prompt with timeout
		console.log('Calling Claude API...');

		// Create a timeout promise
		const timeoutPromise = new Promise((_, reject) => {
			setTimeout(() => reject(new Error('API call timed out after 60 seconds')), 60000);
		});

		// Create the API call promise
		const apiCallPromise = anthropic.messages.create({
			model: 'claude-sonnet-4-5',
			max_tokens: 4096,
			messages: [
				{
					role: 'user',
					content: `You are a crew generator for a WW2 aviation game. Generate a crew based on this description: "${description}"

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks, no explanations.

Requirements:
- Generate an appropriate number of crew members (if not specified, generate 5-10)
- MAXIMUM 10 crew members total - never generate more than 10
- All birth dates must be before 1922 (valid format: YYYY-MM-DD)
- Use authentic names appropriate for the nationality/squadron mentioned
- Class must be either "AirCrew" or "BaseCrew"
- For AirCrew: Role must be one of: Pilot, Gunner, Navigator, BombAimer, FlightEngineer, RadioOperator
- For BaseCrew: Job must be one of: AAFCook, FieldMechanic, FieldEngineer, RAFMedic, AAFLabour
- Skill ranks must be 0-6 (only for AirCrew)
- Gender must be "Male" or "Female"
- Create brief but authentic biographies (2-3 sentences)
- Add "Ethnicity" field: Based on the nationality/description, specify the ethnicity/appearance
  Valid values: "European", "African", "Asian", "MiddleEastern", "Hispanic", "Mixed"
  Examples: Polish → European, Tuskegee Airmen → African, Japanese → Asian

Return a JSON array with this EXACT structure:
[
  {
    "FirstName": "Jan",
    "LastName": "Kowalski",
    "Nickname": "Eagle",
    "BirthDate": "1918-05-15",
    "Gender": "Male",
    "Ethnicity": "European",
    "Class": "AirCrew",
    "Role": "Pilot",
    "Job": "None",
    "Biography": {
      "en": "Brief biography here..."
    },
    "SkillRanks": {
      "Flying": 4,
      "Shooting": 3,
      "Bombing": 2,
      "Endurance": 5,
      "Engineering": 2,
      "Navigating": 3
    }
  }
]

Generate the crew now:`
				}
			]
		});

		// Race the API call against the timeout
		const message = await Promise.race([apiCallPromise, timeoutPromise]);

		console.log('Claude API response received');

		// Extract JSON from response
		let crewData;
		try {
			const responseText = message.content[0].text;
			console.log('Response text length:', responseText.length);
			// Try to parse directly first
			crewData = JSON.parse(responseText);
			console.log('Successfully parsed JSON directly');
		} catch (parseError) {
			console.log('Direct JSON parse failed, trying to extract from markdown:', parseError.message);
			// If direct parse fails, try to extract JSON from markdown code blocks
			const responseText = message.content[0].text;
			const jsonMatch = responseText.match(/```(?:json)?\s*(\[[\s\S]*?\])\s*```/);
			if (jsonMatch) {
				crewData = JSON.parse(jsonMatch[1]);
				console.log('Extracted JSON from markdown code block');
			} else {
				// Try to find any JSON array
				const arrayMatch = responseText.match(/\[[\s\S]*\]/);
				if (arrayMatch) {
					crewData = JSON.parse(arrayMatch[0]);
					console.log('Extracted JSON array from response');
				} else {
					console.error('Could not extract JSON. Response text:', responseText.substring(0, 500));
					throw new Error('Could not extract valid JSON from response');
				}
			}
		}

		// Validate it's an array
		if (!Array.isArray(crewData)) {
			console.error('Response is not an array:', typeof crewData);
			throw new Error('Response is not an array');
		}

		// Limit to maximum 10 crew members
		if (crewData.length > 10) {
			console.log(`Limiting crew from ${crewData.length} to 10 members`);
			crewData = crewData.slice(0, 10);
		}

		console.log('Successfully parsed crew data, count:', crewData.length);

		// Map ethnicity to skin color ranges
		// Skin palette: 0=Very Light, 1=Light, 2=Light Medium, 3=Medium, 4=Olive, 5=Brown, 6=Dark Brown
		const ethnicityToSkinRange = {
			'European': [0, 2],     // Very Light to Light Medium
			'African': [5, 6],       // Brown to Dark Brown
			'Asian': [1, 3],         // Light to Medium
			'MiddleEastern': [3, 4], // Medium to Olive
			'Hispanic': [2, 4],      // Light Medium to Olive
			'Mixed': [0, 6]          // Any skin tone
		};

		// Transform and enrich crew data with random appearance
		const enrichedCrew = crewData.map((member) => {
			// Get gender and ethnicity to generate matching character
			const gender = member.Gender || 'Male';
			const ethnicity = member.Ethnicity || 'European';

			// Get appropriate skin color range based on ethnicity
			const skinColorRange = ethnicityToSkinRange[ethnicity] || [0, 6];

			console.log(`Generating ${ethnicity} character with skin range:`, skinColorRange);

			const randomCharacter = generateRandomCharacter(gender, {
				skinColorRange: skinColorRange
			});

			// Ensure proper metadata structure
			const metadata = {
				Id: crypto.randomUUID(),
				CreatorName: member.CreatorName || '',
				FirstName: member.FirstName || 'Unknown',
				LastName: member.LastName || '',
				Nickname: member.Nickname || '',
				BirthDate: member.BirthDate || '1920-01-01',
				Gender: gender,
				Class: member.Class || 'AirCrew',
				Job: member.Job || 'None',
				Role: member.Role || 'Pilot',
				Biography: member.Biography || { en: '' },
				SkillRanks: member.SkillRanks || {
					Flying: 0,
					Shooting: 0,
					Bombing: 0,
					Endurance: 0,
					Engineering: 0,
					Navigating: 0
				}
			};

			return {
				character: randomCharacter,
				metadata
			};
		});

		console.log('Returning enriched crew, count:', enrichedCrew.length);
		return json({
			crew: enrichedCrew,
			count: enrichedCrew.length,
			replaceExisting
		});
	} catch (error) {
		console.error('Crew generation error:', error);
		console.error('Error stack:', error.stack);
		console.error('Error name:', error.name);
		console.error('Error message:', error.message);

		// Log Anthropic-specific error details if available
		if (error.status) {
			console.error('Anthropic API status:', error.status);
		}
		if (error.error) {
			console.error('Anthropic API error details:', JSON.stringify(error.error, null, 2));
		}

		return json(
			{
				error: 'Failed to generate crew',
				details: error.message,
				type: error.name
			},
			{ status: 500 }
		);
	}
}
