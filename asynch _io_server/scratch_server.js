var dgram = require('dgram');
var util = require('util');


var MAGIC = 0xC461;
var VERSION = 1;
var SERVER_PORT = 33333;


// create datagram (UDP) socket for IPv4 traffic
var serverSocket = dgram.createSocket('udp4');

// register event handlers
// fires when socket starts listening for incoming packets
serverSocket.on('listening', function() {
	var address = serverSocket.address();
	util.log('UDP Server listening on ' + address.address + ":" + address.port);
});

// fires when a packet arrives
serverSocket.on('message', function(message, remote){
	util.log(remote.address + ':' + remote.port + ' - ' + message);
	// check the magic number and version number
	
	serverSocket.send(message, 0 , message.length, remote.port, remote.address);
});

// Enable traffic by binding to a port
// (not specifying a host/IP in this call means all IPs for this system)
serverSocket.bind(SERVER_PORT);

// Register stdin handlers
// Fires when data is available on stdin
process.stdin.on('readable', function(){
	var chunk = process.stdin.read();
	if (chunk !== null){
		if ()
	}
})

process.stdin.on('end', function(){
util.log('shutdown requested');
process.exit();
});
