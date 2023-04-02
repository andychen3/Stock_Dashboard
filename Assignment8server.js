const zmq = require('zeromq'); 

async function runServer() {
  const sock = new zmq.Reply();
  

  await sock.bind('tcp://*:3001');

    console.log('Server is listening on port 3001');

    for await (const [msg] of sock) {
      const message = msg.toString();
      console.log(`Received request: ${message}`);
      console.log('Sending csv file url...');
      
      function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }
      
      async function wait() {
        await sleep(3000);
      }
      
      wait();
      
      const csvFile = 'https://raw.githubusercontent.com/andychen3/CS361/main/ticker.csv';
      await sock.send(csvFile);
      
    }
}


runServer();