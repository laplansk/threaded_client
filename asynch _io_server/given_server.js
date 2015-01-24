#!/usr/bin/node

var dgram = require('dgram');
var util = require('util');


var SERVER_PORT = 33333;
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
    sessions[sess_id][3] = setTimeout(function(){startGoodBye(sess_id);}, 50000);
}

function startGoodBye(sess_id){
    send(Command.GOODBYE, sess_id, function(sess_id){
        clearTimeout(sessions[sess_id][3]);
        process.stdout.write("0x" + sess_id.toString(16) + " ");
        process.stdout.write("Session closed\n");
        delete sessions[sess_id];
    });
}


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
    // prepare GOODBYE message
 /*   var message = new Buffer(12);
	message.writeUInt16BE(MAGIC, 0);
	message.writeUInt8(VERSION, 2);
	message.writeUInt8(Command.GOODBYE, 3);
	message.writeUInt32BE(session_info[2], 4);
	message.writeUInt32BE(sess_no, 8);*/

    // TODO get header ready - no data
    send(Command.GOODBYE, session_no, function(){
        delete map[session_no];
        shutDown(map);
        }
);
    //server.send(goodbyeMessage, 0, goodbyeMessage.length, session_info[1], session_info[0]);
  //  shutDown(map);
}

// Verify a P0P header
function verify(received_magic, received_version) {
    if (received_magic == MAGIC && received_version == VERSION){
        return true;
    } else {
        return false;
    }
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

            } else {
                // create new session, respond with HELLO, start timer
                sessions[sess_id] = [client.address, client.port, 0, -2];
                //console.log("event handler : " + sessions[sess_id]);
                send(Command.HELLO, sess_id, function(sess_id){
                    process.stdout.write("0x" + sess_id.toString(16) + " ");
                    process.stdout.write("[" + sessions[sess_id][2] + "] ");
                    process.stdout.write("Session created\n");
                    startTimer(sess_id);
                });
            }
        }
        else if (command == Command.DATA) {
            if(sess_id in sessions){
                data = message.toString('utf-8', 12, message.length);
                sessions[sess_id][2]++;
                send(Command.ALIVE, sess_id, function(sess_id){
                    process.stdout.write("0x" + sess_id.toString(16) + " ");
                    process.stdout.write("[" + sessions[sess_id][2] + "] ");
                    process.stdout.write(data + "\n");
                    startTimer(sess_id);
                });
            }
        }
    }
});

// an array to hold sessions: {[session_id] -> [address, port, seqNo, timer]}
var sessions = [];

server.bind(SERVER_PORT);

process.stdin.resume();

//listen for input
process.stdin.on('data', function(chunk){
    input = chunk.toString()
    if (input == 'q') {
        // send GOODBYE to ALL clients with open sessions, then terminate
        shutDown(sessions);
    }
});

// On EOF
process.stdin.on('end', function() {
    // send GOODBYE to all clients with open sessions, then terminate
    util.log("shutdown requested");
    shutDown(sessions);
});