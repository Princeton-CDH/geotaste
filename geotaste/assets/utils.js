


function list_is_negation(vals) {
    console.log('list_is_negation <-',vals,ensureArray(vals));
    let res = (ensureArray(vals).length && (ensureArray(vals)[0]=='~'))
    console.log('list_is_negation ->',res);
    return res;
}


function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseInt(str));
}

function bool(obj) {
    // Check for falsy values or the equivalent of Python's None
    if (!obj) return false;

    // Check for numbers (including NaN)
    if (typeof obj === 'number') return !isNaN(obj) && obj !== 0;

    // Check for strings
    if (typeof obj === 'string') return obj.length > 0;

    // Check for arrays or arguments object
    if (Array.isArray(obj) || Object.prototype.toString.call(obj) === '[object Arguments]') return obj.length > 0;

    // Check for objects (including null, which is already handled above)
    if (typeof obj === 'object') return Object.keys(obj).length > 0;

    // Check for functions
    if (typeof obj === 'function') return true;

    // For all other cases, return true as they are truthy in JavaScript
    return true;
}




function processQueryParamValue(val) {
    console.log('processValue <-',val);
    // Check for numeric range indicated by double underscore "__"
    let res = [];
    if (val.includes('--')) {
        let [start, end] = val.split('--').map(Number);
        if (!isNaN(start) && !isNaN(end) && start < end + 1) {
            // Generate range [start, start+1, ..., end-1]
            let res = Array.from({ length: end - start + 1}, (_, i) => start + i);
            res.pop();
            return res;
        }
    }
    // Split non-numeric strings by "_"
    else if (val.includes('_')) {
        res = val.split('_').map(asIntIfPoss); // Handle mixed string and numeric values
    } else {
        // Single numeric value or single string
        res = [asIntIfPoss(val)];
    }
    console.log('processValue ->',res);
    return res
}




function getQueryParams(searchStr) {
    // This function should parse the query string and return an object
    // where each key is a query parameter name, and the value is an array of values.
    // Placeholder implementation:
    const urlSearchParams = new URLSearchParams(searchStr);
    return Array.from(urlSearchParams.keys()).reduce((acc, key) => {
        acc[key] = urlSearchParams.getAll(key);
        return acc;
    }, {});
}

function asIntIfPoss(value) {
    // Convert value to an integer if possible, otherwise return the original value
    const num = parseInt(value, 10);
    return isNaN(num) ? value : num;
}






function rejoinSep(value) {
    // Assuming rejoinSep is a function that formats the value. Implement it according to your logic.
    // This is a placeholder implementation.
    let new_val = value.slice();
    let posneg='';
    let out='';
    if(list_is_negation(value)) {
        new_val = value.slice(1);
        posneg='~';
    }
    console.log(new_val);
    if(new_val.length > 1) {
        [first,last] = [new_val[0], new_val[new_val.length - 1]];
        if(isNumeric(first) && isNumeric(last)) {
            [first2,last2] = sortedFirstAndLast(new_val);
            out=first2.toString().concat('--').concat((parseInt(last2)+1).toString());
            console.log(out);
        }
    } else {
        out=Array.isArray(new_val) ? new_val.join('_') : new_val;
    }
    return posneg.concat(out)
}


function sortedFirstAndLast(arr) {
    // Convert strings to numbers, sort the array in ascending order, and then map back to strings if necessary
    const sortedArr = arr.map(Number).sort((a, b) => a - b).map(String);
    
    if (sortedArr.length === 0) {
      // If the array is empty, return an empty array
      return [];
    } else if (sortedArr.length === 1) {
      // If the array has only one element, return an array with that element twice
      return [sortedArr[0], sortedArr[0]];
    } else {
      // Return an array containing the first and last elements of the sorted array
      return [sortedArr[0], sortedArr[sortedArr.length - 1]];
    }
  }
function ensureArray(input) {
    // Check if the input is an array and return it directly
    if (Array.isArray(input)) {
      return input;
    }
  
    // Check if the input is a non-empty string and return it in an array
    if (typeof input === 'string' && input.length > 0) {
      return [input];
    }
  
    // Return an empty array for empty strings or any other input types
    return [];
  }
  


  function pretty_format_string(str) {
    // Replace underscores with spaces
    const stringWithSpaces = str.replace(/_/g, ' ');
    
    // Capitalize the first letter of the entire string and make sure the rest is in lowercase
    const formattedString = stringWithSpaces.charAt(0).toUpperCase() + stringWithSpaces.slice(1).toLowerCase();
    
    return formattedString;
}


function filters_are_active(filter_data) {
    console.log('filters_are_active <-',filter_data)
    let res= (Object.keys(filter_data).length>0);
    console.log('filters_are_active ->',res);
    return res;
}



function mergeSubcomponentFilters(...objs) {
    // Merge all objects into a single object
    return Object.assign({}, ...objs);
  }
  


  function getSelectedRecordsFromFigureSelectedData(selectedData = {}, quant = null) {
    if (!selectedData || !Array.isArray(selectedData.points) || selectedData.points.length === 0) {
        return [];
    }

    const pointsData = selectedData.points;

    function getRecordId(d, keys = ['label', 'location']) {
        if (!d) return null;
        for (let k of keys) {
            if (d.hasOwnProperty(k)) {
                return d[k];
            }
        }
        console.error('What is the record id here? --> ' + JSON.stringify(d));
        return null; // Returning null if none of the keys match
    }

    function asIntIfPoss(value) {
        const num = parseInt(value, 10);
        return isNaN(num) ? value : num;
    }

    let selectedRecords = pointsData.map(d => getRecordId(d))
                                     .filter(x => x != null);

    // Apply asIntIfPoss if quant is true
    if (quant === true) {
        selectedRecords = selectedRecords.map(val => val.trim()).filter(val => val).map(asIntIfPoss)
    }

    selectedRecords.sort(); // Simple alphabetical or numerical sort

    return selectedRecords;
}
