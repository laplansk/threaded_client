var dgram = require('dgram');
var util = require('util');

// currently active timeout timer
var timer = null;

//-------------------------------------
// set up datagram socket
//-------------------------------------

// Server's port is hardwired
var SERVER_PORT = 33333;

// Obtain server's host from command line arg
if (process.argv.length != 3){
    util.log("Usage: nodejs client server_name");
    process.exit(1);
}

var serverHost = process.argv[2];

// create datagram socket, IPv4
var clientSocket = dgram.createSocket('udp4');

//-------------------------------------
// set up socket and stdin handlers
//--------------------------------------

// When a packet arrives on it, print what it contains
clientSocket.on('mesasge', function(chunk) {
    chunk = chuck.toString().trim;
    var message = new Buffer(chunk);
    clientSocket.send(message, 0, message.length, SERVER_PORT, serverHost, function(err, bytes) {
        if(err) throw error;
    });
    if (timer == null){
        timer = setTimeout(function(){
            util.log("No Response");
            timer = null;
        }, 5000);
    }
})