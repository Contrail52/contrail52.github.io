var db

function canUseCache(config, db) {
	return config.cache && typeof window !== "undefined" && typeof db !== "undefined";
}

function openCache(config){
	 const version = 1;
	 
	if (config.cache && typeof window !== "undefined") {
		const request = window.indexedDB.open("scarlet-league-phb", version);
        return new Promise((resolve, reject) => {
            request.onerror = (event) => {
                console.log('IndexedDB not available')
                reject()
            }
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                const transaction = event.target.transaction;
                let objectStore;

                if (!db.objectStoreNames.contains('cache')) {
                    objectStore = db.createObjectStore("cache", { autoIncrement: false });
                    console.log('Object store "cache" created');
                } else {
                    objectStore = transaction.objectStore("cache");
                }

                if (!objectStore.indexNames.contains("database_hash_index")) {
                    objectStore.createIndex("database_hash_index", "meta.database_hash", { unique: false });
                    console.log('Index "database_hash_index" created');
                }
            }
            request.onsuccess = (event) => {
                db = event.target.result;
                console.log('db opened')
                resolve(db)
            }
            request.onversionchange = (event) => {
                db.close()
                reject()
            }
            request.onblocked = (event) => {
                db.close()
                reject()
            }
        });
	}
}

function getFromDB(objectStore, url) {
	return new Promise((resolve, reject) => {
		const cachedObject = objectStore.get(url);
		cachedObject.onsuccess = () => resolve(cachedObject.result);
		cachedObject.onerror = () => reject(cachedObject.error);
	});
}

async function loadResource(config, url){
	if (!url.startsWith(config.databasePath)) { // Only try to pull from the expected database locations
		url = `${config.databasePath}${url}`;
	}
	if (canUseCache(config, db)) {
		const transaction = db.transaction("cache", "readonly");
		const objectStore = transaction.objectStore("cache");
		const data = await getFromDB(objectStore, url);
		if (data) {
			console.log(`Read from cache ${url}`);
			return data;
		}
		else {
			return await loadUrl(config, url);
		}
	}
	else {
		return await loadUrl(config, url);
	}
}

async function loadUrl(config, url) {
	const response = await fetch(url);
	const body = await response.json();
	if (response.status === 200) {
		if (canUseCache(config, db)) {
			const hash = config.hash;
			body.meta = { database_hash: hash };
			const transaction = db.transaction("cache", "readwrite");
			const objectStore = transaction.objectStore("cache");
			const request = objectStore.add(body, url);
			request.onsuccess = () => {
				console.log(`Object cached ${url}`);
			}
			request.onerror = () => {
				console.log(request.error);
			}
		}
	}
	
	return body;
}

function sizeCache(config) {
	if (canUseCache(config, db)) {
		return new Promise((resolve, reject) => {
			const transaction = db.transaction("cache", "readwrite");
			const objectStore = transaction.objectStore("cache");
			const request = objectStore.count();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => reject(request.error);
		});
	}
	else {
		return Promise.reject(new Error("Cache not available"));
	}
}

async function invalidateCache(config) {
	if (canUseCache(config, db)) {
		return new Promise((resolve, reject) => {
			const transaction = db.transaction("cache", "readwrite");
			const objectStore = transaction.objectStore("cache");
			const index = objectStore.index("database_hash_index");
            const range1 = IDBKeyRange.upperBound(config.hash, true);
            const range2 = IDBKeyRange.lowerBound(config.hash, true);
			const request1 = index.getAllKeys(range1);
			
			request1.onsuccess = () => {
				const keys = request1.result;
				keys.forEach(pk => {
					objectStore.delete(pk);
					console.log(`invalidated ${pk}`);
				});
			};
			request1.onerror = () => reject(new Error(request1.error));
			const request2 = index.getAllKeys(range2);
			
			request2.onsuccess = () => {
				const keys = request2.result;
				keys.forEach(pk => {
					objectStore.delete(pk);
					console.log(`invalidated ${pk}`);
				});
			};
			request2.onerror = () => reject(new Error(request2.error));
			resolve(true);
		});
	}
	else {
		throw new Error("Cache not available");
	}
}

function clearCache(config) {
	if (canUseCache(config, db)) {
		return new Promise((resolve, reject) => {
			const transaction = db.transaction("cache", "readwrite");
			const objectStore = transaction.objectStore("cache");
			const request = objectStore.clear();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => reject(request.error);
		});
	}
	else {
		return Promise.reject(new Error("Cache not available"));
	}
}

export { loadResource, openCache, sizeCache, clearCache, invalidateCache };