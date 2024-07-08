const fs = require('fs');
const express=require('express');
const bodyParser= require('body-parser');
const { spawn } = require('child_process');
const app =express();
const os = require('os');
const { exec } = require('child_process');
const { parse } = require("csv-parse");
app.use(express.static('public'));
var SpellChecker = require('simple-spellchecker');

app.use(express.json());
app.use(bodyParser.urlencoded({extended: false}));

if (process.platform ==='darwin'){
    var prompt ='curl -X POST "https://accounts.spotify.com/api/token" \
                    -H "Content-Type: application/x-www-form-urlencoded" \
                    -d "grant_type=client_credentials&client_id=8cf61d77bb564cbcb05eccb597654f65&client_secret=f62e3fbb26f04c5daab99835aac9c536"'
                    
    var volume_up = 'osascript -e "set volume output volume ((output volume of (get volume settings)) + 20)"' 
    var volume_down = 'osascript -e "set volume output volume ((output volume of (get volume settings)) - 20)"'
    var mute = 'osascript -e "set volume with output muted"'
    var unmute = 'osascript -e "set volume without output muted"'               

}              
app.post('/musicSearch',async (req,res)=>{
    console.log(req);
    exec(prompt,async(error, stdout, stderr) => {
        const songName=req.body.song_name
        const artistName=req.body.artist
        const opt = req.body.op
        console.log(stdout);
        var token = (JSON.parse(stdout).access_token)
        var accessToken = token
        console.log(`access token: ${accessToken}`);
        console.log(artistName)

        const searchQuery = encodeURIComponent(`${songName} artist:${artistName}`);
        const searchURL = `https://api.spotify.com/v1/search?q=${searchQuery}&type=track`;
        try {
            const response = await fetch(searchURL, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            const data =await response.json();
            console.log(data)
            if (!data.tracks || !data.tracks.items || data.tracks.items.length === 0) {
                console.error('Error: No track found');
                res.status(404).send('No track found');
                return;
            }
            const firstTrackURI = data.tracks.items[0].uri;
            console.log('Song URI:', firstTrackURI);

            if (opt=='close'){
                if (process.platform ==='darwin'){
                    exec(`killall Spotify`,async(error, stdout, stderr) => {
                    });
                    
                }
              
            }
            else if(opt=='open'){
                if (process.platform ==='darwin'){
                    exec(`killall Spotify`,async(error, stdout, stderr) => { });
                    setTimeout(function() {exec(`open "spotify:track:${firstTrackURI}"`,async(error, stdout, stderr) => {});}, 1000);
                } 
  
            }
        } catch (error) {
            console.error('Error:', error);
            
        }

        res.status(200).send(JSON.stringify('Successful'));
    })

});


app.post('/volumeAdjust',async (req,res)=>{
    const operation = req.body.op
    if (operation == 'mute'){
        if (process.platform === 'darwin'){
            
            setTimeout(function() {exec(mute,async(error, stdout, stderr) => {});}, 3000);
        } 
    }
    if (operation == 'unmute'){
        if (process.platform === 'darwin'){
            exec(unmute,async(error, stdout, stderr) => {});
        }
    }
    if (operation == 'volumeUp'){
        if (process.platform === 'darwin'){

            exec(volume_up,async(error, stdout, stderr) => {});
            
        }
    }
    if (operation == 'volumeDown'){
        if (process.platform === 'darwin'){

            exec(volume_down,async(error, stdout, stderr) => {});

        }
    }
});


const userHome = os.homedir();
var username = "";
if (userHome.includes('/')) {
    username = userHome.split('/').pop();
    console.log(username);
}
else {
    username = userHome.split('\\').pop();
    console.log(username);
} 

app.get('/ChatBot', (req,res) => {
    res.sendFile('/public/GUI.html', { root: __dirname });
});

app.get('/ChatBot/username', (req, res) => {
    res.send({ username: username });
});

const path = require('path');
const { error } = require('console');
const pythonFilePath = path.join(__dirname, 'python_main.py');
console.log(pythonFilePath)

fs.access(pythonFilePath, fs.constants.F_OK, (err) => {
    if (err) {
      console.error(`File ${pythonFilePath} does not exist`);
    } else {
      console.log(`File ${pythonFilePath} exists`);
    }
  });

app.post('/trv',async (req,res)=>{
    const response = req.body
    console.log(response)

    const columnNames = ['vel', 'latitude', 'longitude'];
    const csvHeader = columnNames.join(',') + '\n';

    const csvData = `${response.vel},${response.latitute},${response.longitude}\n`;

    fs.writeFile('./CurrenCoordinates&velocity.csv', csvHeader + csvData, (err) => {
        if (err) {
            console.error('Error writing to CSV file:', err);
        } else {
            console.log('Data has been written to data.csv');
        }
    });
    res.send(response)
    
});

app.get('/resetContingency',async (req,res)=>{
    const response = req.body
    console.log(response)

    const columnNames = ['Station1','Station2','BlockageType'];
    const csvHeader = columnNames.join(',');

    fs.writeFile('./contingencies_details.csv', csvHeader , (err) => {
        if (err) {
            console.error('Error writing to CSV file:', err);
        } else {
            console.log('Data has been written to data.csv');
        }
    });
    res.send(response)
    
});

app.post('/ChatBot', (req,res)=>{
    const user_input=req.body.userInput;
    var split_User_input = user_input.split(' ')

    //Reading intention.json
    var JSONPatterns = []
    fs.readFile("./intentions.json",(err,data)=>{
        if (err) throw err;
        // Converting to JSON 
        const users = JSON.parse(data); 
        const JsonKeys = Object.keys(users)
        
        for (k = 0;k<JsonKeys.length-1;k++){
            //console.log(users[JsonKeys[k]].patterns);
            JSONPatterns.push((users[JsonKeys[k]].patterns))
        }
        JSONPatterns=[...new Set ((JSONPatterns.flat(Infinity).map(str => str.split(' ')).flat(Infinity)))]
    

        // reading sentences.txt
        const fileContents = fs.readFileSync('./sentences.txt', 'utf8');
        const words = [...new Set (fileContents.split(/\s+/))];// only unique values


        const FinalChekListTypo = words.concat(JSONPatterns)
        console.log(FinalChekListTypo);
        // Auto spelling check and typo fix.
        for(let i =0 ;i<split_User_input.length ;i++){
            SpellChecker.getDictionary("en-US", function(err, dictionary) {
                if(!err) {
                    var misspelled = ! dictionary.spellCheck(split_User_input[i]);
                    if(misspelled) {
                        var suggestions = dictionary.getSuggestions(split_User_input[i]);
                        console.log("suggestions: ",suggestions)
                        if(suggestions.length>0){
                            for (let j = 0 ; j<suggestions.length ; j++){
                                if(FinalChekListTypo.includes(suggestions[j])){
                                    split_User_input[i] = suggestions[j]
                                    console.log("Updatedted Splitted User İnput ",split_User_input)
                                }
                            }
                        }
                    }
                }
            }); 
        }
    
        setTimeout(function(){
            const reunion=split_User_input.join(' ')
            console.log(reunion)
            const python = spawn('python', ['chatbot_conversation.py', JSON.stringify(reunion)]);// sending the request (user input) to the python file to generate responses based on that.
            python.stdout.on('data', (data) => {// fetching outputs of print statements tothe node terminal.
                console.log(`***Python script's print outputs:***\n ${data}`);
            });   
            python.on('error', (err) => {//error detection in the python code.
                console.error('Python  error:', err);
            }); 

            python.on('close', (code) => {// fetching the results from python code
                const result = fs.readFileSync('output.txt', 'utf-8');
                console.log(result)
                res.send({message: result.toString('utf-8')});
            });
        },1000)
    })  
});

app.get('/currentJourney', async (req, res) => {
    const data = [];

    const parseCSV = () => {
        return new Promise((resolve, reject) => {
            fs.createReadStream("./current_journey_info.csv")
                .pipe(parse({ delimiter: ",", from_line: 2 }))
                .on("data", (row) => {
                    data.push(row);
                })
                .on("error", (error) => {
                    console.error(error.message);
                    reject(error);
                })
                .on("end", () => {
                    console.log("parsed csv data:");
                    console.log(data);
                    resolve(data);
                });
        });
    };

    const readFile = (path) => {
        return new Promise((resolve, reject) => {
            fs.readFile(path, 'utf-8', (err, fileData) => {
                if (err) {
                    console.error(err);
                    reject(err);
                } else {
                    console.log(fileData);
                    resolve(fileData);
                }
            });
        });
    };

    try {
        await new Promise(resolve => setTimeout(resolve, 6000)); // Simulate the timeout

        const csvData = await parseCSV();
        const fileData = await readFile('./train_fare_scraper_counter.txt');

        const final_data = [fileData, csvData];
        console.log(final_data);
        res.send(final_data);
    } catch (error) {
        console.error('Error processing the request:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/contingencies',async (req,res)=>{
    const data = []
    setTimeout(()=>{
        fs.createReadStream("./contingencies_details.csv")
                .pipe(parse({ delimiter: ",", from_line: 2 }))
                .on("data", (row) => {
                    data.push(row);
                })
                .on("error", (error) => {
                    console.error(error.message);
                    reject(error);
                })
                .on("end", () => {
                    console.log("parsed csv data:");
                    console.log(data);
                    res.send(data);
                });
    },10)
});

app.get('/returnCounter',async (req,res)=>{
    setTimeout(()=>{
        fs.readFile('./return_counter.txt' , 'utf-8' , (err,data)=>{
            if (err) {
                console.error(err);
                return;
              }
              console.log(data);
              res.send(data)
        });
    },2000)
});
 
app.listen(5501);
console.log('Server is listening on http://localhost:5501/chatbot');