class Config {
	constructor(config={}){
		this.databasePath = "{DATABASE_DIRECTORY}";
		this.hash = "{DATABASE_HASH_VALUE}";
		this.cache = true;
	}
}

export { Config }