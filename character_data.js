const data = {
    // A GUID of the character
    "Id": "0f8fad5b-d9cb-469f-a165-70867728950e",
    // Name of the person who created the character
    "CreatorName": "Random Guy",
    // First name, coming from the user
    "FirstName": "John",
    // Last name, coming from the user
    "LastName": "Doe",
    // Nickname, coming from the user - only used if `Class` is `AirCrew`
    "Nickname": "Chief",
    // Birth date, formatted as YYYY-MM-DD, needs to be before 1922
    "BirthDate": "1920-01-01",
    // Male|Female
    "Gender": "Male",
    // BaseCrew|AirCrew
    "Class": "AirCrew",
    // Used if `Class` is `BaseCrew`, otherwise `None`
    // Can also be `None` if there is no job preference (i.e. character can appear in-game with any job)
    // None|AAFCook|FieldMechanic|FieldEngineer|RAFMedic|AAFLabour
    "Job": "None",
    // Used if `Class` is `AirCrew`, otherwise `None`
    // None|Pilot|Gunner|Navigator|BombAimer|FlightEngineer|RadioOperator
    "Role": "Pilot",
    // Description of the character's background
    // Can have multiple language versions (but currently only the `en` one will be used)
    "Biography": {
        "en": "Part of original Demo crew."
    },
    // Skill ranks - currently only applicable if `Class` is `AirCrew`
    // Each rank can have a value from 0 to 6 (both inclusive)
    "SkillRanks": {
        "Flying": 0,
        "Shooting": 0,
        "Bombing": 0,
        "Endurance": 0,
        "Engineering": 0,
        "Navigating": 0
    },
    // Index and variant for each body part.
    // The filename of each body part image is formatted in the following way: <name>_<index>_<variant>
    // Eg. hair_09_02 means body part = hair, index = 9, variant = 2
    // If a particular body part should not be present, it should use the index/variant of -1
    // Only parts marked so can use the -1 value
    "EditorData": {
        // Body shape / torso (PortraitSprites/17_Body_Skin/body_##_00.png)
        // Valid combinations (both genders use the same sprites):
        //   Index 00: Variants 0  -> body_00_00 (Thin)
        //   Index 01: Variants 0  -> body_01_00 (Average)
        // Original meaning: 0: Thin | 1: Average | 2: Bulky | 3: Fat
        "BodyShapeIndex": 1,

        // Accessory (PortraitSprites/3_Accessory_Accessory/accessory_##_##.png)
        // Can be -1 for "no accessory".
        // Valid combinations (no gender-specific sprites, same for Male/Female):
        //   Index 00: Variants 0, 1, 2, 3
        //   Index 01: Variants 0
        //   Index 02: Variants 0, 1, 2, 3
        //   Index 03: Variants 0
        "Accessory": {
            "Index": 2,
            "Variant": 2
        },

        // Blemish (PortraitSprites/1_Blemish_Skin/blemish_##_00.png)
        // Can be -1 for "no blemish".
        // Valid combinations (same for Male/Female):
        //   Index 00: Variants 0
        //   Index 01: Variants 0
        //   Index 02: Variants 0
        "Blemish": {
            "Index": 1,
            "Variant": 0
        },

        // Nose (PortraitSprites/2_Nose_Skin/nose_##_##.png)
        // Cannot be -1.
        // Valid combinations per gender:
        //   Index 00: Variants 0 (M), 1 (M), 2 (M)
        //   Index 01: Variants 0 (M), 1 (M)
        //   Index 02: Variants 0 (M)
        //   Index 03: Variants 0 (M)
        //   Index 04: Variants 0 (M), 1 (M)
        //   Index 05: Variants 0 (M+F), 1 (M+F)
        //   Index 06: Variants 0 (M+F), 1 (M+F)
        //   Index 07: Variants 0 (M+F), 1 (M+F)
        //   Index 08: Variants 0 (F), 1 (F)
        //   Index 09: Variants 0 (F), 1 (F)
        //   Index 10: Variants 0 (F)
        //   Index 11: Variants 0 (F)
        //   Index 12: Variants 0 (F), 1 (F)
        //   Index 20: Variants 0 (F)
        //   Index 21: Variants 0 (F)
        "Nose": {
            "Index": 6,
            "Variant": 0
        },

        // Eyebrows (PortraitSprites/4_Eyebrows_Hair/eyebrows_##_##.png)
        // Cannot be -1.
        // Valid combinations per gender:
        //   Index 00: Variants 0 (M), 1 (M)
        //   Index 01: Variants 0 (M+F)
        //   Index 02: Variants 0 (M+F), 1 (M+F)
        //   Index 03: Variants 0 (M), 1 (M)
        //   Index 04: Variants 0 (M+F)
        //   Index 05: Variants 0 (M+F), 1 (M+F), 2 (M+F)
        //   Index 06: Variants 0 (M), 1 (M)
        //   Index 07: Variants 0 (M)
        //   Index 08: Variants 0 (F)
        //   Index 09: Variants 0 (F)
        //   Index 10: Variants 0 (F)
        "Eyebrows": {
            "Index": 5,
            "Variant": 1
        },

        // Eyes (PortraitSprites/5_Eyes_Eye/eyes_##_##(.png / _female.png))
        // Cannot be -1.
        // Valid combinations per gender:
        //   Index 00: Variants 0 (M), 1 (M)
        //   Index 01: Variants 0 (M)
        //   Index 02: Variants 0 (M+F)
        //   Index 03: Variants 0 (M+F), 1 (M+F), 2 (M+F), 3 (M+F), 4 (M+F), 5 (M+F)
        //   Index 04: Variants 0 (M), 1 (M)
        //   Index 05: Variants 0 (M)
        //   Index 06: Variants 0 (M)
        //   Index 07: Variants 0 (M+F), 1 (M+F)
        //   Index 08: Variants 0 (F), 1 (F), 2 (F), 3 (F)
        //   Index 09: Variants 0 (F), 1 (F)
        //   Index 10: Variants 0 (F)
        //   Index 11: Variants 0 (F)
        //   Index 12: Variants 0 (F), 1 (F)
        "Eyes": {
            "Index": 3,
            "Variant": 4
        },

        // Moustache (PortraitSprites/7_Moustache_Hair/moustache_##_##.png)
        // Can be -1 for "no moustache".
        // Valid combinations (same for Male/Female, but you’ll usually
        // only allow them for male characters in your editor logic):
        //   Index 00: Variants 0, 1
        //   Index 01: Variants 0, 1
        //   Index 02: Variants 0, 1
        //   Index 03: Variants 0, 1, 2
        //   Index 04: Variants 0, 1, 2
        "Moustache": {
            "Index": 3,
            "Variant": 1
        },

        // Beard (PortraitSprites/8_Beard_Hair/beard_##_##.png)
        // Can be -1 for "no beard".
        // Valid combinations:
        //   Index 00: Variants 0, 1, 2
        //   Index 20: Variants 0
        "Beard": {
            "Index": -1,
            "Variant": -1,
        },

        // Mouth (PortraitSprites/9_Mouth_Lip/mouth_##_00.png)
        // Can be -1 for "no mouth".
        // This will only be used if `Moustache.Index` is -1.
        // Valid combinations (same for Male/Female):
        //   Index 00: Variants 0
        //   Index 01: Variants 0
        //   Index 02: Variants 0
        //   Index 03: Variants 0
        //   Index 04: Variants 0
        //   Index 05: Variants 0
        //   Index 06: Variants 0
        //   Index 07: Variants 0
        //   Index 08: Variants 0
        //   Index 09: Variants 0
        //   Index 10: Variants 0
        //   Index 11: Variants 0
        //   Index 12: Variants 0
        //   Index 13: Variants 0
        //   Index 14: Variants 0
        //   Index 15: Variants 0
        "Mouth": {
            "Index": -1,
            "Variant": -1
        },

        // Hair (front) (PortraitSprites/10_Hair_Hair/hair_##_##(.png / _female.png))
        // Can be -1 for "no hair".
        // Valid combinations per gender:
        //   Index 00: Variants 0 (M), 1 (M), 2 (M)
        //   Index 01: Variants 0 (M), 1 (M)
        //   Index 02: Variants 0 (M), 1 (M), 2 (M)
        //   Index 03: Variants 0 (M), 1 (M), 2 (M)
        //   Index 04: Variants 0 (M)
        //   Index 05: Variants 0 (M), 1 (M)
        //   Index 06: Variants 0 (M), 1 (M), 2 (M)
        //   Index 07: Variants 0 (F), 1 (F), 2 (F), 3 (F)
        //   Index 08: Variants 0 (F), 1 (F)
        //   Index 09: Variants 0 (F), 1 (F), 2 (F), 3 (F)
        //   Index 10: Variants 0 (F), 1 (F)
        //   Index 11: Variants 0 (F), 1 (F)
        //   Index 12: Variants 0 (F)
        //   Index 13: Variants 0 (F)
        //
        // Interpretation:
        //   (M)   = only base sprite exists.
        //   (F)   = only _female sprite exists (no base file).
        //   (M+F) = both versions exist.
        // From the game’s POV all of these combos are valid for both genders,
        // you just get different art where _female exists.
        "Hair": {
            "Index": 9,
            "Variant": 3
        },

        // Detail / skin overlays (PortraitSprites/11_Detail_Skin and 12_Detail_Skin)
        // Can be -1 for "no detail".
        // Folder 11_Detail_Skin (indices 0–9):
        //   Index 00: Variants 0
        //   Index 01: Variants 0
        //   Index 02: Variants 0
        //   Index 03: Variants 0
        //   Index 04: Variants 0
        //   Index 05: Variants 0
        //   Index 06: Variants 0
        //   Index 07: Variants 0
        //   Index 08: Variants 0
        //   Index 09: Variants 0
        // Folder 12_Detail_Skin (indices 10–20):
        //   Index 10: Variants 0
        //   Index 11: Variants 0
        //   Index 12: Variants 0
        //   Index 13: Variants 0
        //   Index 14: Variants 0
        //   Index 15: Variants 0
        //   Index 16: Variants 0
        //   Index 17: Variants 0
        //   Index 18: Variants 0
        //   Index 19: Variants 0
        //   Index 20: Variants 0
        "Detail": {
            "Index": 15,
            "Variant": 0
        },

        // Headshape (PortraitSprites/13_Headshape_Skin/headshape_##_##(.png / _female.png))
        // Cannot be -1.
        // Valid combinations per gender:
        //   Index 00: Variants 0 (M), 1 (M)
        //   Index 01: Variants 0 (M)
        //   Index 02: Variants 0 (M)
        //   Index 03: Variants 0 (M)
        //   Index 04: Variants 0 (M)
        //   Index 05: Variants 0 (M)
        //   Index 06: Variants 0 (M)
        //   Index 07: Variants 0 (M), 1 (M)
        //   Index 08: Variants 0 (F), 1 (F), 2 (F)
        //   Index 09: Variants 0 (F), 1 (F)
        //   Index 10: Variants 0 (F)
        //   Index 11: Variants 0 (F)
        //   Index 12: Variants 0 (F)
        //   Index 13: Variants 0 (F)
        //   Index 14: Variants 0 (F)
        //   Index 15: Variants 0 (F)
        "Headshape": {
            "Index": 7,
            "Variant": 0
        },

        // Ears (PortraitSprites/15_Ears_Skin/ears_##_00.png)
        // Cannot be -1.
        // Valid combinations (same for Male/Female):
        //   Index 00: Variants 0
        //   Index 01: Variants 0
        //   Index 02: Variants 0
        //   Index 03: Variants 0
        //   Index 04: Variants 0
        //   Index 05: Variants 0
        //   Index 06: Variants 0
        //   Index 07: Variants 0
        "Ears": {
            "Index": 4,
            "Variant": 0
        },

        // The color index is an index in the preconfigured array of available colors for each type
        // Valid colors: "000000", "6F4429", "9F7F44"
        "AccessoryColorIndex": 1,
        // Valid colors: "F5CCBA", "E0BAB4", "ECA696", "CF9895", "CA7E5B", "9C7162", "A65C3F", "765543", "603121", "4B342E"
        "SkinColorIndex": 4,
        // Valid colors: "73361F", "994E2A", "673719", "7B511F", "6F3B17", "09090A", "29150C", "482518", "684834", "442B28", "AE9D88", "AC8C7A", "8E6E51", "C2A370", "735145", "685F5F", "383434", "817778"
        "HairColorIndex": 2,
        // Valid colors: "333C82", "2B3041", "2E2E2E", "2E5224", "4E5224", "5B4708", "5E351B", "76442D", "3F2417", "29180F", "1D0E06", "261F1B"
        "EyeColorIndex": 1
    }

    }

}