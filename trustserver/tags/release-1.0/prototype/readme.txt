To use the prototype:

run `TrustServer.py` - This will start the update and query listeners.  In the program, you may enter commands.  'people' will print the lookup table.  'quit' will terminate the server program. any other command will print a list of possible help commands.

in another terminal:
run `sample_loader.py` -- This will populate the server with sample information
run `TrustClient.py localhost 50000`  -- This will open a client connection for query
 
Queries are of the form 'source:sink:subject'.  So, for example, on the sample data, the following ought to work (there are more, and you can use your own sample data):
'Schamp:Goforth:default'
'Laing:Crowe:cooking'
'Schamp:Laing:default'
'Laing:Goforth:ohio'

Currently, the server uses the following function to compute trust across a path:  .5-(.5-pathScore)*linkScore
It's just an example, as I haven't determined the best infrastructure for applying different strategies yet.

The server will build a path using the specified subject whenever possible, but if no subject-specific link is available, it will use the default.

If no path exists, it will print an appropriate message.