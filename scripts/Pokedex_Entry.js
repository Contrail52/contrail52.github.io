/* 
This is the primary script for autmatically building the inner HTML data for
the Pokedex entry webpage.

Utilizes https://pokeapi.co/ and https://github.com/PokeAPI/pokeapi-js-wrapper.
*/

import {Pokedex} from "https://cdn.jsdelivr.net/gh/pokeapi/pokeapi-js-wrapper@2.0.2/src/index.js";
import {PHB_Loader} from "/scripts/phb_loader.js";

/* Utility Functions */
async function fetchJSON(filepath){
	return await fetch(filepath).then(response => {
		if (!response.ok){
			throw new Error('HTTP Error! Status: ${response.status}');
		}
		return response.json();
	});
}
function setElementData(elementID, data){
	document.getElementById(elementID).innerHTML = data;
}
function formatStringArray(arr){
	const size = arr.length;
	
	if (size == 0){
		return "--";
	}
	else {
		var arr2 = [];
		for (const [index, str] of arr.entries()){
			arr2.push(str.charAt(0).toUpperCase() + str.slice(1));
		}
		return arr2.reduce(function(a, b) { return a + ", " + b; });
	}
	return null;
}

function titleCase(str, delimiter){
	var splitStr = str.toLowerCase().split(delimiter);
	for (var i = 0; i < splitStr.length; i++){
		splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
	}
	return splitStr.join(delimiter);
}

/* PHB Pokedex Database Functions */
function formatASIText(asi){
	const mod = Math.floor((asi - 10)/2);
	if (mod < 0){
		return String(asi).padStart(2, " ") + "( " + mod + ")";
	}
	else if (mod >= 10){
		return String(asi).padStart(2, " ") + "(+" + mod + ")";
	}
	else{
		return String(asi).padStart(2, " ") + "( +" + mod + ")";
	}
	return null;
}
async function processPHBDatabase(phb_pokemon_data, entry_name){
	// Process Title Info
	setElementData("Species-Name", phb_pokemon_data[entry_name].Name);
	setElementData("Pokedex-Number", "#"+phb_pokemon_data[entry_name].ID);
	
	// Update all non-table element information
	setElementData("Classification", phb_pokemon_data[entry_name].Classification);
	setElementData("SR", phb_pokemon_data[entry_name].SR);
	setElementData("Minimum_Level", phb_pokemon_data[entry_name].Min_Level);
	setElementData("Hit_Dice", phb_pokemon_data[entry_name].Hit_Dice);
	setElementData("Movement", phb_pokemon_data[entry_name].Movement);
	setElementData("Senses", phb_pokemon_data[entry_name].Senses);
	
	setElementData("Proficient_Skills", formatStringArray(phb_pokemon_data[entry_name].Skills));
	setElementData("Saving_Throws", formatStringArray(phb_pokemon_data[entry_name].Saves));
	setElementData("Evolution_Text", phb_pokemon_data[entry_name].Evolution);
	
	// Process Stat Data
	setElementData("HP_Value", String(phb_pokemon_data[entry_name].Stats.HP).padEnd(7, " "));
	setElementData("AC_Value", String(phb_pokemon_data[entry_name].Stats.AC).padEnd(7, " "));
	setElementData("STR_Value", formatASIText(phb_pokemon_data[entry_name].Stats.STR));
	setElementData("DEX_Value", formatASIText(phb_pokemon_data[entry_name].Stats.DEX));
	setElementData("CON_Value", formatASIText(phb_pokemon_data[entry_name].Stats.CON));
	setElementData("INT_Value", formatASIText(phb_pokemon_data[entry_name].Stats.INT));
	setElementData("WIS_Value", formatASIText(phb_pokemon_data[entry_name].Stats.WIS));
	setElementData("CHA_Value", formatASIText(phb_pokemon_data[entry_name].Stats.CHA));
	
	document.getElementById("HP_Bar").value = phb_pokemon_data[entry_name].Stats.HP;
	document.getElementById("AC_Bar").value = phb_pokemon_data[entry_name].Stats.AC;
	document.getElementById("STR_Bar").value = phb_pokemon_data[entry_name].Stats.STR;
	document.getElementById("DEX_Bar").value = phb_pokemon_data[entry_name].Stats.DEX;
	document.getElementById("CON_Bar").value = phb_pokemon_data[entry_name].Stats.CON;
	document.getElementById("INT_Bar").value = phb_pokemon_data[entry_name].Stats.INT;
	document.getElementById("WIS_Bar").value = phb_pokemon_data[entry_name].Stats.WIS;
	document.getElementById("CHA_Bar").value = phb_pokemon_data[entry_name].Stats.CHA;
}


/* PokeAPI Database Functions */
function formatHeight(height){
	return String(height / 10) + "m";
}
function formatWeight(weight){
	return String(weight / 10) + "kg";
}
function formatGenderRatio(gender_rate){ // Gender rate is chance of being female in eighths
	switch(gender_rate){
		case 0: return "100% M";
		case 1: return "87.5% M / 12.5% F";
		case 2: return "75% M / 25% F";
		case 3: return "62.5% M / 37.5% F";
		case 4: return "50% M / 50% F";
		case 5: return "37.5% M / 62.5% F";
		case 6: return "25% M / 75% F";
		case 7: return "12.5% M / 87.5% F";
		case 8: return "100% F";
		default: return "--";
	}
}
function parseTypeChart(type1, type2){ // Compute weaknesses, resistances, and immunities
	// Type is an integer as defined by https://pokeapi.co/
	//  0: Undefined
	//  1: Normal
	//  2: Fighting
	//  3: Flying
	//  4: Poison
	//  5: Ground
	//  6: Rock
	//  7: Bug
	//  8: Ghost
	//  9: Steel
	// 10: Fire
	// 11: Water
	// 12: Grass
	// 13: Electric
	// 14: Psychic
	// 15: Ice
	// 16: Dragon
	// 17: Dark
	// 18: Fairy
	//							  ???  NRM  FGT  FLY  PSN  GND  RCK  BUG  GHT  STL  FIR  WTR  GRS  ELC  PSY  ICE  DRG  DRK  FRY
	const defense_type_chart = [[ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 2.0],
								[ 1.0, 1.0, 0.5, 1.0, 1.0, 0.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 0.5, 1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5],
								[ 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 0.0, 1.0, 2.0, 1.0, 1.0, 1.0],
								[ 1.0, 0.5, 2.0, 0.5, 0.5, 2.0, 1.0, 1.0, 1.0, 2.0, 0.5, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 0.5, 2.0, 1.0, 0.5, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
								[ 1.0, 0.0, 0.0, 1.0, 0.5, 1.0, 1.0, 0.5, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0],
								[ 1.0, 0.5, 2.0, 0.5, 0.0, 2.0, 0.5, 0.5, 1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 0.5, 0.5, 0.5, 1.0, 0.5],
								[ 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 0.5, 1.0, 0.5, 0.5, 2.0, 0.5, 1.0, 1.0, 0.5, 1.0, 1.0, 0.5],
								[ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 2.0, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 1.0, 2.0, 2.0, 0.5, 1.0, 2.0, 1.0, 1.0, 2.0, 0.5, 0.5, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 1.0, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 2.0, 1.0],
								[ 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0],
								[ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 1.0, 2.0, 2.0, 1.0, 2.0],
								[ 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.5, 2.0],
								[ 1.0, 1.0, 0.5, 1.0, 2.0, 1.0, 1.0, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.5, 1.0]];
	const type_names = ["???", "Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy"];
	
	const type_matchup = defense_type_chart[type1].map((a, i) => a * defense_type_chart[type2][i]);
	
	var weaknesses = [];
	var resistances = [];
	var immunities = [];
	for (const [index, mult] of type_matchup.entries()){
		if (mult == 0){
			immunities.push(type_names[index]);
		}
		else if (mult < 1.0){
			resistances.push(type_names[index]);
		}
		else if (mult > 1.0){
			weaknesses.push(type_names[index]);
		}
	}
	
	return [formatStringArray(weaknesses), formatStringArray(resistances), formatStringArray(immunities)];
}
function formatEggGroups(egg_groups){
	var groups = [];
	for (const egg_group_object of egg_groups){
		groups.push(egg_group_object.name);
	}
	return formatStringArray(groups);
}
function getTypes(type_object){
	const type_names = {"normal": 1, 
						"fighting": 2, 
						"flying": 3, 
						"poison": 4, 
						"ground": 5, 
						"rock": 6, 
						"bug": 7, 
						"ghost": 8, 
						"steel": 9, 
						"fire": 10, 
						"water": 11, 
						"grass": 12, 
						"electric": 13, 
						"psychic": 14, 
						"ice": 15, 
						"dragon": 16, 
						"dark": 17, 
						"fairy": 18};
	
	var type1 = type_names[type_object[0].type.name];
	var type2 = 0
	if (type_names.length > 1){
		type2 = type_names[type_object[1].type.name];
	}
	return [type1, type2];
}
function getGenera(genera_array){
	for (const genera_object of genera_array){
		if (genera_object.language.name == "en"){
			return "The " + genera_object.genus;
		}
	}
	return null;
}
function getFlavorText(flavor_text_array){
	for (const flavor_text of flavor_text_array){
		if (flavor_text.language.name == "en"){ // Just grab the first english one right now
			return flavor_text.flavor_text.replace(/[^a-zA-Z'%.!?’ é]/g, " "); // Some entries have special characters in them. They need to be removed.
		}
	}
	return null;
}
function getAbilityTitle(ability_text_array){
	for (const ability_text of ability_text_array){
		if (ability_text.language.name == "en"){ // Just grab the first english one right now
			return ability_text.name.replace(/[^a-zA-Z'%.!?’ é]/g, " "); // Some entries have special characters in them. They need to be removed.
		}
	}
	return null;
}

async function processPokeAPIDatabase(pokemon, pokemon_species){
	// Process Title Info
	setElementData("Genera", getGenera(pokemon_species.genera));
	setElementData("Flavor-Text", getFlavorText(pokemon_species.flavor_text_entries));
	
	// Update Sprite Image
	if (Math.floor(Math.random() * 4096) == 0){
		document.getElementById("Sprite").src = pokemon.sprites.other["official-artwork"].front_shiny;
	}
	else{
		document.getElementById("Sprite").src = pokemon.sprites.other["official-artwork"].front_default;
	}
	
	// Process Type Data
	const types = getTypes(pokemon.types);
	document.getElementById("Type-1").src = "/images/type_icons/" + pokemon.types[0].type.name + ".png";
	document.getElementById("Type-1").alt = pokemon.types[0].type.name;
	if (pokemon.types.length > 1){
		document.getElementById("Type-2").src = "/images/type_icons/" + pokemon.types[1].type.name + ".png";
		document.getElementById("Type-2").alt = pokemon.types[1].type.name;
	}
	else{
		document.getElementById("Type-2").setAttribute("style", "display:none");
	}
	
	// Process Dex Entry Data
	setElementData("Height", formatHeight(pokemon.height));
	setElementData("Weight", formatWeight(pokemon.weight));
	setElementData("Gender_Ratio", formatGenderRatio(pokemon_species.gender_rate));
	setElementData("Egg_Groups", formatEggGroups(pokemon_species.egg_groups));
	
	// Process Type Matchup Data
	const type_matchups = parseTypeChart(types[0], types[1]);
	setElementData("Weaknesses", type_matchups[0]);
	setElementData("Resistances", type_matchups[1]);
	setElementData("Immunities", type_matchups[2]);
}

function formatAbilityText(phb_ability_data, ability_name, ability_title){
	const ability_link = "<a href=\"../Abilitydex/Ability_Entry.html?name=" + ability_name + "\">" + ability_title + "</a>";
	const description = phb_ability_data[ability_name].Description;
	return ability_link + " - " + description;
}

async function processAbilities(pokedex, pokemon, phb_pokemon_data, phb_ability_data, entry_name){
	const current_abilities = pokemon.abilities;
	const past_abilities = pokemon.past_abilities;
	
	for (const current_ability of current_abilities){
		const ability_name = current_ability.ability.name;
		if (ability_name !== null){
			//const ability_title = titleCase(titleCase(ability_name, '-'), ' ');
			const ability_api_data = await pokedex.getAbilityByName(ability_name);
			const ability_title = getAbilityTitle(ability_api_data.names);
			if (current_ability.is_hidden == true){
				document.getElementById("hidden_ability_div").style = "display:inline";
				document.getElementById("Ability_Name_HA").style = "display:inline";
				//document.getElementById("Ability_Name_HA").href = "../Abilitydex/Ability_Entry.html?name=" + ability_name;
				const div_data = formatAbilityText(phb_ability_data, ability_name, ability_title);
				setElementData("Ability_Name_HA", div_data);
			}
			else{
				document.getElementById("Ability_Name_" + current_ability.slot).style = "display:inline";
				//document.getElementById("Ability_Name_" + current_ability.slot).href = "../Abilitydex/Ability_Entry.html?name=" + ability_name;
				const div_data = formatAbilityText(phb_ability_data, ability_name, ability_title);
				setElementData("Ability_Name_" + current_ability.slot, div_data);
			}
		}
	}
	
	if (past_abilities.length !== 0){
		for (const past_ability of past_abilities[0].abilities){
			const ability = past_ability.ability;
			if (ability !== null) {
				const ability_name = ability.name;
				if (ability_name !== null){
					const ability_api_data = await pokedex.getAbilityByName(ability_name);
					const ability_title = getAbilityTitle(ability_api_data.names);
					
					document.getElementById("special_abilities_div").style = "display:inline";
					document.getElementById("Special_Ability_Name_" + past_ability.slot).style = "display:inline";
					const div_data = formatAbilityText(phb_ability_data, ability_name, ability_title);
					setElementData("Special_Ability_Name_" + past_ability.slot, div_data);
				}
			}
		}
	}
	
	// Rockruff requires it's own special case for Own Tempo, because of course it does
	if (entry_name == "rockruff"){
		const ability_name = "own-tempo";
		const ability_api_data = await pokedex.getAbilityByName(ability_name);
		const ability_title = getAbilityTitle(ability_api_data.names);
		document.getElementById("Ability_Name_3").style = "display:inline";
		const div_data = formatAbilityText(phb_ability_data, ability_name, ability_title);
		setElementData("Ability_Name_3", div_data);
	}
}

// Entry Point

// Retrieve the pokedex ID from the URL search parameters
const params = new URLSearchParams(window.location.search);
const entry_name = params.get("name");

// Fetch PHB JSON Database
const PHB_Cache = await PHB_Loader.init();
PHB_Cache.invalidateCache();
const phb_pokemon_data = await PHB_Cache.loadPHBPokedex("Scarlet_League_3.0");
const phb_ability_data = await PHB_Cache.loadPHBAbilitydex("Scarlet_League_3.0");
const phb_attack_data = await PHB_Cache.loadPHBAttackdex("Scarlet_League_3.0");
//const phb_pokemon_data = await fetchJSON("/src/databases/Scarlet_League_3.0/Pokedex/Pokedex.json");
//const phb_ability_data = await fetchJSON("/src/databases/Scarlet_League_3.0/Abilitydex/Abilitydex.json");
//const phb_attack_data = await fetchJSON("/src/databases/Scarlet_League_3.0/Attackdex/Attackdex.json");

// Fetch PokeAPI Database
//config = new Config();
const pokedex = await Pokedex.init();// Done to automatically cache the data from the request
const pokemon = await pokedex.getPokemonByName(entry_name);
const pokemon_species = await pokedex.getPokemonSpeciesByName(entry_name);

processPHBDatabase(phb_pokemon_data, entry_name);
processPokeAPIDatabase(pokemon, pokemon_species);

processAbilities(pokedex, pokemon, phb_pokemon_data, phb_ability_data, entry_name);