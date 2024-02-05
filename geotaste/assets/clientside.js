


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
                 .flatMap(processQueryParamValue) // Use processValue to handle all specified formats
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
                        thisvalstr = thisvalstr.concat(x).concat(" to ").concat((parseInt(y)+1).toString())
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



function negate_filter_data(filter_data) {
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

function intersect_and_negate(nclick, ...filters_data) {
    let filter_d = mergeSubcomponentFilters(...filters_data);
    let filter_d_neg = negate_filter_data(filter_d);
    return filter_d_neg;
}

function process_incoming_data(data,keys) {
    console.log('incoming data',data);
    let key2out={};
    for(const key of keys) {
        key2out[key]=window.dash_clientside.no_update;
    }
    for(const key of Object.keys(data)) {
        if(key in key2out) {
            key2out[key] = {};
            key2out[key][key]=data[key]; // kinda weird but we want each to have its key
        }
    }
    let out = [];
    for(const key of keys) {
        out.push(key2out[key]);
    }
    console.log('out',out);
    return out;
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
        loadQueryParam:loadQueryParam,
        intersect_and_negate:intersect_and_negate
    }
});