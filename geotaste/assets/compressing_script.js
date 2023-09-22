window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        decompress: function(json_gz) {
            let compressedData = Uint8Array.from(atob(json_gz), (c) => c.charCodeAt(0));
            let decompressedData = pako.inflate(compressedData, { to: "string" });
            let jsonObject = JSON.parse(decompressedData);
            console.log('received:', jsonObject);
            return jsonObject;
        }
    }
});