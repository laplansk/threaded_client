#!/usr/bin/node

// Comments only for differences from ../node.js-Simple/server.js
var dgram = require('dgram');
var util = require('util');
var readline = require('readline');
var fs = require('fs');

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

// send Goodbye Message to a single client
function sendGoodbye(session_id) {
// TODO send goodbye message to client associated with session_id
// double check that session_id is valid?
}



function sendGoodbye(map){

    //  base case = no more sessions, so exit
    if isEmpty(map){
        process.exit();
    }

    // get info from one of remaining sessions, then delete it from the map
    var session_no
    var session_info;
    for(var sess_no in map){
        session_no = sess_no;
        session_info = map[sess_no];
        delete map[sess_no];
        break;
    }

    // Send GOODBYE message to client associated with this session
    // prepare GOODBYE message
    var message = new Buffer(12);
	message.writeUInt16BE(MAGIC, 0);
	message.writeUInt8(VERSION, 2);
	message.writeUInt8(Command.GOODBYE, 3);
	message.writeUInt32BE(session_info[2], 4);
	message.writeUInt32BE(sess_no, 8);

    // TODO get header ready - no data
    server.send(goodbyeMessage, 0, goodbyeMessage.length, session_info[1], session_info[0]);
    sendGoodbye(map);
}

// Verify a P0P header
function verify(received_magic, received_version) {
    if (received_magic == MAGIC && received_version == VERSION){
        return true;
    } else {
        return false;
    }
}

// Handle input from stdin
function stdinListen() {
	var stdin = process.stdin;
	stdin.resume();
	stdin.on('data',function(chunk){
	    input = chunk.toString()
	    if (line == 'q') {
	        // send GOODBYE to ALL clients with open sessions, then terminate
			sendGoodbye(sessions);
		}
	})

	// On EOF
	stdin.on('end', function() = {
	    // send GOODBYE to all clients with open sessions, then terminate
	    sendGoodbye(sessions);
	});
	}
}

server.on('listening', function () {
    var address = server.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

server.on('message', function (message, client_port) {

    // parse header
    if (buf.length < 12) {
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
        break;
    } else { // process message

        if (/*HELLO*/) {
            // check whether or not session id already exists
            // create session
            // send HELLO back
            // set timer (where will timer be held? in the session?)
        } else if () {

        }
    }
});


// TODO create data structure to store sessions.

// a map to hold sessions: {(session_id -> (address, port, seqNo, timer)}
var sessions = {};

/*

ADD TO MAP

a["key1"] = "value1";
a["key2"] = "value2";

/*

ACCESS MAP

if ("key1" in a) {
   // something
} else {
   // something else
}
*/

server.bind(SERVER_PORT);

process.stdin.on('data', function(chunk){
});

process.stdin.on('end', function() {
    util.log("shutdown requested");
    process.exit(0);
});