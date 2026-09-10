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

function getCurrentRuleset(){
	const url = window.location.href;
	const subdomain = "/web/";
	
	return url.split(subdomain)[1].split("/")[0];
}

export { fetchJSON, setElementData, formatStringArray, getCurrentRuleset };