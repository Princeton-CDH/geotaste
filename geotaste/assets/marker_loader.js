var dwelling_markers;

function decompress_obj(json_gz) {
  let compressedData = Uint8Array.from(atob(json_gz), (c) => c.charCodeAt(0));
  let decompressedData = pako.inflate(compressedData, { to: "string" });
  let jsonObject = JSON.parse(decompressedData);
  console.log('received:', jsonObject);
  return jsonObject;
}

function load_init_data(){
    fetch('/assets/data.markers.compressed.json')
    .then( r => r.text() )
    .then( t => {
      dwelling_markers=decompress_obj(t);
    })
}

function get_dwelling_markers(dwellings, L_or_R='L') {
  var l = [];
  console.log(dwellings);
  for (i = 0; i < dwellings.length; i++) {
      dwelling = dwellings[i];
      dwelling_key = dwelling+"_"+L_or_R;
      dwelling_marker = dwelling_markers[dwelling_key];
      console.log('dwelling_marker',dwelling_key, dwelling_marker);
      l.push(dwelling_marker)
  }
  return l;
}

    // fetch('/assets/data.markers.compressed.json')
    //   .then(response => response.arrayBuffer())
    //   .then(buffer => pako.inflate(new Uint8Array(buffer)))
    //   .then(decompressed => {
    //       let jsonObject = JSON.parse(decompressed);
    //       console.log('received:', jsonObject);
    //       return jsonObject;
    //     // // convert binary data to string
    //     // const decoder = new TextDecoder('utf-8');
    //     // const csv = decoder.decode(decompressed);
    //     // // parse csv with Papa Parse
    //     // Papa.parse(csv, {
    //     // //   delimiter: ',',
    //     //   dynamicTyping: true,
    //     //   skipEmptyLines: true,
    //     //   header: true,
    //     //   complete: function(results) {
    //     //     console.log(results.data);
    //     //   }
    //     // });
    //   })
    //   .catch(error => console.log(error));
  // }


// // // var results = Papa.parse("a,b,c");
// // // console.log(results);

// var combined_data;

// Papa.parse('/assets/combined.mini.csv.gz', {
//     header: true,
//     download: true,
//     dynamicTyping: true,
// 	complete: function(results) {
// 		console.log(results);
//         combined_data = results.data;
// 	}
// });


load_init_data()
