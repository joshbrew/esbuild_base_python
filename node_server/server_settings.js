const settings = {
    debug:false, //print debog messages?
    protocol:'http', //'http' or 'https'. HTTPS required for Nodejs <---> Python sockets. If using http, set production to False in python/server.py as well
    host: 'localhost', //'localhost' or '127.0.0.1' etc.
    port: 8000, //e.g. port 80, 443, 8000
    hotreload: 5000, //hotreload websocket server port
    python: 7000,  //quart server port
    python_node:7001, //websocket relay port (relays messages to client from nodejs that were sent to it by python)
    startpage: 'src/index.html',  //home page
    errpage: 'src/other/404.html', //error page, etc.
    certpath:'node_server/ssl/cert.pem',//if using https, this is required. See cert.pfx.md for instructions
    keypath:'node_server/ssl/key.pem'//if using https, this is required. See cert.pfx.md for instructions
}

exports.settings = settings;