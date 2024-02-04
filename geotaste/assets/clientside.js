

function list_is_negation(vals) {
    console.log('list_is_negation <-',vals,ensureArray(vals));
    let res = (ensureArray(vals).length && (ensureArray(vals)[0]=='~'))
    console.log('list_is_negation ->',res);
    return res;
}


function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseInt(str));
}

DEFAULT_STATE={
    'bearing': 0,
    'lat': 48.85107555543428, 
    'lon': 2.3385039932538567,
    'pitch': 0,
    'zoom': 14,
    'tab': 'map',
    'tab2': 'arrond'
}

function track_state(fdL, fdR, tab, tab2) { // , zoom, center) {
    console.log('track_state <-',fdL, fdR, tab, tab2);
    let state = {};
    Object.keys(fdL).forEach(k => state[k] = rejoinSep(fdL[k]));
    Object.keys(fdR).forEach(k => state[k + '2'] = rejoinSep(fdR[k]));
    state['tab'] = tab;
    state['tab2'] = tab2;
    console.log('state',state);
    state = Object.fromEntries(
        Object.entries(state).filter(([k, v]) => v && DEFAULT_STATE[k] !== v)
    );
    if (Object.keys(state).length === 0) return '';
    let ostr = new URLSearchParams(state).toString();
    let res = ostr;
    if(ostr) {
        res = '?'.concat(res);
    } else {
        res = window.dash_clientside.no_update;
    }
    console.debug(`track_state -> ${res}`);
    return res;
}


function processValue(val) {
    console.log('processValue <-',val);
    // Check for numeric range indicated by double underscore "__"
    let res = [];
    if (val.includes('--')) {
        let [start, end] = val.split('--').map(Number);
        if (!isNaN(start) && !isNaN(end) && start < end +1) {
            // Generate range [start, start+1, ..., end]
            res = Array.from({ length: end - start + 1 }, (_, i) => start + i);
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





function loadQueryParam(searchStr, appBegun) {
    let out = new Array(6).fill(window.dash_clientside.no_update);
    
    if (appBegun || !searchStr) {
        return out;
    }

    const params = getQueryParams(searchStr); // Assuming getQueryParams is implemented elsewhere
    // Only allow one query param per param name
    const singleParams = Object.keys(params).reduce((acc, key) => {
        acc[key] = params[key][0];
        return acc;
    }, {});
    console.debug(`params = ${JSON.stringify(singleParams)}`);

    let isContrast = 'contrast' in singleParams && singleParams['contrast'] !== 'False';
    let fdL = {}, fdR = {}, tab = 'map', tab2 = 'arrond';

    Object.entries(singleParams).forEach(([k, v]) => {
        if (!v) return;
        if (k === 'tab') {
            tab = v;
        } else if (k === 'tab2') {
            tab2 = v;
        } else {
            let fd = k.endsWith('2') ? fdR : fdL;
            k = k.endsWith('2') ? k.slice(0, -1) : k;
            const isNeg = v.startsWith('~');
            if (isNeg) v = v.slice(1);
            // fd[k] = (isNeg ? ['~'] : []).concat(
            //     v.split('_').map(val => val.trim()).filter(val => val).map(asIntIfPoss)
            // );
            fd[k] = (isNeg ? ['~'] : []).concat(
                v.split('_')
                 .map(val => val.trim())
                 .filter(val => val)
                 .flatMap(processValue) // Use processValue to handle all specified formats
            );
        }
    });

    function negateFd(fd) {
        return Object.fromEntries(
            Object.entries(fd).map(([k, vl]) => [k, vl && vl[0] !== '~' ? ['~'].concat(vl) : vl.slice(1)])
        );
    }

    // Negate other fields if contrast else manually set
    if (isContrast) {
        fdR = { ...negateFd(fdL), ...fdR };
    }

    out = [fdL, fdR, tab, tab2, true, false];
    console.debug(`--> ${JSON.stringify(out)}`);
    return out;
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
            out=first2.toString().concat('--').concat(last2.toString());
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
  



function describe_filters(filter_data) {
    console.log('describe_filters',filter_data);
    let desc_parts = [];
    if(filters_are_active(filter_data)) {
        console.log('filters data now',filter_data);
        for (const key of Object.keys(filter_data)) {
            console.log('key',key,filter_data[key]);
            let val_list = ensureArray(filter_data[key]);
            if(val_list.length) {
                let is_neg = false;
                if(list_is_negation(val_list)) {
                    is_neg = true;
                    val_list = val_list.slice(1);
                }
                let thisvalstr = pretty_format_string(key).concat(" is ");
                if(is_neg) { thisvalstr = thisvalstr.concat("not ") }
                if(val_list.length == 1) {
                    thisvalstr=thisvalstr.concat(val_list[0]);
                } else {
                    if(isNumeric(val_list[0]) && isNumeric(val_list[val_list.length-1])) {
                        const [x,y] = sortedFirstAndLast(val_list);
                        thisvalstr = thisvalstr.concat(x).concat(" to ").concat(y)
                    } else {
                        console.log('val_list',val_list, val_list.join);
                        thisvalstr = thisvalstr.concat(val_list.join(", "));
                    }
                }
                desc_parts.push(thisvalstr)
            }
        }
    }
    let out = desc_parts.join(" and ")
    console.log('describe_filters ->',out,filter_data);
    return out;
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

function get_component_desc_and_is_open(filter_data) {
    console.log('get_component_desc_and_is_open <-',filter_data);    
    if(!filters_are_active(filter_data)) {
        var res = ["",false];
    } else {
        let valstr = describe_filters(filter_data);
        console.log('valstr2',valstr);
        var res = [valstr, true];
    }
    console.log('get_component_desc_and_is_open ->',res);    
    return res;
}

function decompress_json_gz(json_gz) {
    let compressedData = Uint8Array.from(atob(json_gz), (c) => c.charCodeAt(0));
    let decompressedData = pako.inflate(compressedData, { to: "string" });
    let jsonObject = JSON.parse(decompressedData);
    console.log('received:', jsonObject);
    return jsonObject;
}

function get_negation_btn_msg_and_style(filter_data, is_open) {
    console.log('get_negation_btn_msg_and_style <-',filter_data, is_open)
    let button_msg = "Switch to negative matches";
    let style = {"display":"none"}
    for (const key of Object.keys(filter_data)) {
        const val_list = ensureArray(filter_data[key]);
        if(val_list.length) {
            style = {"display":"block"};
            if(list_is_negation(val_list)) {
                button_msg = "Switch to positive matches";
            }
        }
    }
    let res=[button_msg,style];
    console.log('get_negation_btn_msg_and_style ->',res);
    return res;
}

function toggle_showhide_btn(nclick1,nclick2,isOpen) { 
    console.log('toggle_showhide_btn',nclick1,nclick2,isOpen)
    let isOpenNow=!isOpen;
    let btn = "";
    if(isOpenNow) { btn = "[–]"; } else { btn = "[+]" }
    return [isOpenNow, btn];
}

function negate_filter_data(nclick,filter_data) {
    console.log('negate_filter_data',filter_data);
    for (const key of Object.keys(filter_data)) {
        const val_list = ensureArray(filter_data[key]);
        if(val_list.length) {
            if(list_is_negation(val_list)) {
                filter_data[key] = val_list.slice(1);
            } else {
                filter_data[key] = ["~"].concat(val_list);
            }
        }
    }
    return filter_data;
}

function mergeSubcomponentFilters(...objs) {
    // Merge all objects into a single object
    return Object.assign({}, ...objs);
  }
  

function intersect_subcomponent_filters(...args) {
    console.log('intersect_subcomponent_filters <-',args);
    const filtersD = args.slice(0, -1);
    const oldData = args[args.length - 1];
    const intersectedFilters = mergeSubcomponentFilters(...filtersD);
    console.log('intersect_subcomponent_filters 2',intersectedFilters);
  
    // Comparing objects in JavaScript requires a custom function since === doesn't do deep comparison
    if (JSON.stringify(oldData) === JSON.stringify(intersectedFilters)) {
        console.log('no change');
        return window.dash_clientside.no_update;
    } else {
        console.log('changed');
        console.log(JSON.stringify(oldData));
        console.log(JSON.stringify(intersectedFilters));
        
    }
  
    // console.debug(`[YourComponentName] subcomponent filters updated, triggered by: ${ctx.triggeredId}, incoming = ${JSON.stringify(filtersD)}, returning ${JSON.stringify(intersectedFilters)}, which is diff from ${JSON.stringify(oldData)}`);
    console.log('intersected',intersectedFilters);
    return intersectedFilters;
  }



window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        decompress_json_gz: decompress_json_gz,
        get_component_desc_and_is_open: get_component_desc_and_is_open,
        get_negation_btn_msg_and_style: get_negation_btn_msg_and_style,
        negate_filter_data: negate_filter_data,
        toggle_showhide_btn: toggle_showhide_btn,
        describe_filters: describe_filters,
        intersect_subcomponent_filters: intersect_subcomponent_filters,
        track_state:track_state,
        loadQueryParam:loadQueryParam
    }
});