import { loadResource, openCache, sizeCache, clearCache, invalidateCache } from '/scripts/cache_manager.js'
import { Config } from '/scripts/config.js'

export class PHB_Loader {
	constructor(config) {
		this.config = config;
	}
	
	static async init(config) {
		config = new Config(config);
		await openCache(config);
		//await invalidateCache(config);
		return new PHB_Loader(config);
	}
	
	getConfig() {
		return this.config;
	}
	
	getCacheLength() {
		return sizeCache(this.config);
	}
	
	clearCache() {
		return clearCache(this.config);
	}
	
	invalidateCache() {
		return invalidateCache(this.config);
	}
	
	resource(path) {
		if (typeof path === "string") {
			return loadResource(this.config, path);
		}
		else if (Array.isArray(path)) {
			return Promise.all(path.map(p => loadResource(this.config, p)));
		}
		else {
			return "String or Array is required";
		}
	}
	
	loadPHBPokedex(database) {
		if (database) {
			if (typeof database === "string") {
				return loadResource(this.config, database + "/Pokedex/Pokedex.json");
			}
		}
	}
	
	loadPHBAbilitydex(database) {
		if (database) {
			if (typeof database === "string") {
				return loadResource(this.config, database + "/Abilitydex/Abilitydex.json");
			}
		}
	}
	
	loadPHBAttackdex(database) {
		if (database) {
			if (typeof database === "string") {
				return loadResource(this.config, database + "/Attackdex/Attackdex.json");
			}
		}
	}
}