## Building the server directory

The **server** directory capture all the key elements of your application and can be used with our generic docker image.

To generate that directory, just run the **scripts/build_server.sh** script.

## Building your docker image

Your docker image is simply bundling the **server** directory into a docker image to simplify possible deployment.

To generate that image, just run the **scripts/build_image.sh** script.

## Running your bundle

Just run either `scripts/run_server.sh` or `scripts/run_image.sh` and open your browser to `http://localhost:8080/visualizer.html`