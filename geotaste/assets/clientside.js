
function get_filter_values(filter_data) {
    let vals = [];
    if(filters_are_active(filter_data)) {
        for (const key in filter_data) {
            console.log(key,filter_data[key]);
            vals.push(...filter_data[key]);
        }
    }
    return vals;
}


function list_is_negation(vals) {
    return (vals.length && (vals[0]=='~'))
}

function get_val_str(vals) {
    console.log('get_val_str <-',vals);
    let posneg='';
    if(list_is_negation(vals)) {
        vals=vals.slice(1);
        posneg='~';
    }
    let out = posneg.concat(vals.join(", "));
    console.log('get_val_str ->',out);
    return out;
}

function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseInt(str));
}

function firstAndLast(arr) {
    if (arr.length === 0) {
      // If the array is empty, return an empty array
      return [];
    } else if (arr.length === 1) {
      // If the array has only one element, return an array with that element twice
      return [arr[0], arr[0]];
    } else {
      // Return an array containing the first and last elements of the original array
      return [arr[0], arr[arr.length - 1]];
    }
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

function describe_filters(filter_data) {
    let desc_parts = [];
    if(filters_are_active(filter_data)) {
        for (const key in filter_data) {
            let val_list = filter_data[key];
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
                        thisvalstr = thisvalstr.concat(val_list.join(", "));
                    }
                }
                desc_parts.push(thisvalstr)
            }
        }
    }
    let out = desc_parts.join(" and ")
    console.log('describe_filters ->',out);
    return out;
}

function pretty_format_string(str) {
    // Replace underscores with spaces
    const stringWithSpaces = str.replace(/_/g, ' ');
    
    // Capitalize the first letter of the entire string and make sure the rest is in lowercase
    const formattedString = stringWithSpaces.charAt(0).toUpperCase() + stringWithSpaces.slice(1).toLowerCase();
    
    return formattedString;
}

// vals=[v for v in list(store_data.values())[0]]
    // is_neg=False
    // if vals and vals[0]=='~':
    //     vals = vals[1:]
    //     is_neg=True
    // minval=min(vals) if vals else self.minval
    // maxval=max(vals) if vals else self.maxval
    // o = f'{minval} to {maxval}'
    // return f'~({o})' if is_neg else o

function filters_are_active(filter_data) {
    return (Object.keys(filter_data).length>0);
}

function get_component_desc_and_is_open(filter_data) {
    console.log('valstr',filter_data);    
    if(!filters_are_active(filter_data)) {
        return ["",false];
    } else {
        let valstr = describe_filters(filter_data);
        console.log('valstr2',valstr);
        return [valstr, true];
    }
}

function decompress_json_gz(json_gz) {
    let compressedData = Uint8Array.from(atob(json_gz), (c) => c.charCodeAt(0));
    let decompressedData = pako.inflate(compressedData, { to: "string" });
    let jsonObject = JSON.parse(decompressedData);
    console.log('received:', jsonObject);
    return jsonObject;
}

function get_negation_btn_msg_and_style(filter_data) {
    let button_msg = "Switch to negative matches";
    let style = {"display":"none"}
    for (const key in filter_data) {
        const val_list = filter_data[key];
        if(val_list.length) {
            style = {"display":"block"};
            if(list_is_negation(val_list)) {
                button_msg = "Switch to positive matches";
            }
        }
    }
    return [button_msg,style];
}

function toggle_showhide_btn(nclick1,nclick2,isOpen) { 
    console.log('toggle_showhide_btn',nclick1,nclick2,isOpen)
    let isOpenNow=!isOpen;
    let btn = "";
    if(isOpenNow) { btn = "[–]"; } else { btn = "[+]" }
    return [isOpenNow, btn];
}

function negate_filter_data(nclick,filter_data) {
    for (const key in filter_data) {
        const val_list = filter_data[key];
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


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        decompress_json_gz: decompress_json_gz,
        get_component_desc_and_is_open: get_component_desc_and_is_open,
        get_negation_btn_msg_and_style: get_negation_btn_msg_and_style,
        negate_filter_data: negate_filter_data,
        toggle_showhide_btn: toggle_showhide_btn,
        describe_filters: describe_filters
    }
});