#!/usr/bin/node

var dgram = require('dgram');

var MAGIC = 0xC461
var VERSION = 1

var Command = {
	HELLO : 0,
	DATA : 1,
	ALIVE : 2,
	GOODBYE : 3
};

// This socket will be used to listen and to send to all clients
var server = dgram.createSocket('udp4');

// helper to test whether or not sessions object is empty
function isEmpty(map) {
    for (var name in map) {
        return false;
    }
    return true;
}


// takes a command(ALIVE, GOODBYE, etc.) and a function execute when finished
function send(command, sess_id, callback) {
	var client_address = sessions[sess_id][0];
	var client_port = sessions[sess_id][1];

	// Create header
	var message = new Buffer(12);
	message.writeUInt16BE(MAGIC, 0);
	message.writeUInt8(VERSION, 2);
	message.writeUInt8(command, 3);
	message.writeUInt32BE(sessions[sess_id][2], 4);
	message.writeUInt32BE(sess_id, 8);

    server.send(message, 0, message.length, client_port, client_address, callback(sess_id)); // <- callback = startTimer
}

// this function will reset any timers if they already exist.
function startTimer(sess_id){
    clearTimeout(sessions[sess_id][3]);
    sessions[sess_id][3] = setTimeout(function(){startGoodBye(sess_id);}, 5000);
}

function startGoodBye(sess_id){
    send(Command.GOODBYE, sess_id, function(sess_id){
        clearTimeout(sessions[sess_id][3]);
        process.stdout.write("0x" + sess_id.toString(16) + " ");
        process.stdout.write("Session closed\n");
        delete sessions[sess_id];
    });
}


// send GOODBYE to all open session clients then exit
function shutDown(map){

    //  base case == no more sessions, so exit
    if (isEmpty(map)){
        process.exit();
    }

    // get info from one of remaining sessions, then delete it from the map
    var session_no
    var session_info;
    for(var s in map){
        session_no = s;
        //session_info = map[sess_no];
        // stop timer for this session
        clearTimeout(map[session_no][3]);
        //delete map[sess_no];
        break;
    }

    // Send GOODBYE message to client associated with this session
    send(Command.GOODBYE, session_no, function(){
        delete map[session_no];
        shutDown(map);
        }
    );
}

// Verify a P0P header
function verify(received_magic, received_version) {
    return received_magic == MAGIC && received_version == VERSION
}


server.on('listening', function () {
    var address = server.address();
    console.log('waiting on port ' + address.port + '...');
});

server.on('message', function (message, client) {

    // parse header
    if (message.length < 12) {
		return false;
	}

    var magic_number = message.readUInt16BE(0);
    var version_number = message.readUInt8(2);
    var command = message.readUInt8(3);
    var seqNo = message.readUInt32BE(4);
    var sess_id = message.readUInt32BE(8);

    // check that MAGIC and VERSION are correct
    //if not, exit function/discard/ignore packet
    if(!verify(magic_number, version_number)){
        return;
    } else { // process message
        if (command == Command.HELLO) {
            if (sess_id in sessions){ // message is a duplicate
                console.log("Duplicate Packet");
            } else {
                // create new session, respond with HELLO, start timer
                sessions[sess_id] = [client.address, client.port, 0, -2];
                send(Command.HELLO, sess_id, function(sess_id){
                    process.stdout.write("0x" + sess_id.toString(16) + " ");
                    process.stdout.write("[" + sessions[sess_id][2] + "] ");
                    process.stdout.write("Session created\n");
                    startTimer(sess_id);
                });
            }
        }
        else if (command == Command.DATA) {
            data = message.toString('utf-8', 12, message.length);
            if(sess_id in sessions){
                // Is the packet in the right order or not?
                if(seqNo = sessions[sess_id][2] + 1) { // in order
                    sessions[sess_id][2]++;
                    send(Command.ALIVE, sess_id, function (sess_id) {
                        process.stdout.write("0x" + sess_id.toString(16) + " ");
                        process.stdout.write("[" + sessions[sess_id][2] + "] ");
                        process.stdout.write(data + "\n");
                        startTimer(sess_id);
                    });
                } else {
                    // packet is out of order so print lost packets for the difference
                    var difference = seqNo - sessions[sess_id][2];
                    sessions[sess_id][2] = seqNo;
                    for (var i = sessions[sess_id][2]; i <= seqNo; i++){
                        process.stdout.write("0x" + sess_id.toString(16) + " ");
                        process.stdout.write("[" + i + "] ");
                        process.stdout.write("Lost Packet!\n");
                    }
                }
            }
        }
    }
});

// an array to hold sessions: {[session_id] -> [address, port, seqNo, timer]}
var sessions = [];

var SERVER_PORT = process.argv[2];

server.bind(SERVER_PORT);

process.stdin.resume();

//listen for input
process.stdin.on('data', function(chunk){
    input = chunk.toString()
    if (input === "q") {
        // send GOODBYE to ALL clients with open sessions, then terminate
        shutDown(sessions);
    }
});

// On EOF
process.stdin.on('end', function() {
    // send GOODBYE to all clients with open sessions, then terminate
    shutDown(sessions);
});