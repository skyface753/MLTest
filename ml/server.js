const http = require('http');
const express = require('express');
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const port = 3000;

var app = express();

app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(cookieParser());

app.use( bodyParser.json() );       // to support JSON-encoded bodies
app.use(bodyParser.urlencoded({     // to support URL-encoded bodies
  extended: true
})); 

var cors = require('cors');

app.use(cors());

app.use(function (req, res, next) {
    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', '*');
    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type,Authorization');
    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);
    // Pass to next layer of middleware
    next();
});

var brain = require('brain.js');  
var net = new brain.NeuralNetwork();  
net.train([{input: [{"userid": 1, "videoId": 10}]},              
           {input: [0, 1], output: [1]},            
           {input: [1, 0], output: [1]},            
           {input: [1, 1], output: [0]}]);  


app.get('/input', (req, res) => {
    var likedId = req.body.likedId;
    var newId = net.run([likedId]);
    res.send(newId);
});

var httpServer = http.createServer(app);
httpServer.listen(port);
console.log("Server gestartet");
console.log("Port: " + port);