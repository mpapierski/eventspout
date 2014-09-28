# eventspout

Docker vents router that transmits events as they appear to pre-defined HTTP endpint. You can then match event to a host, and container in your app and do some interesting things.

## Status

Unstable, but works.

## Getting eventspout

Normal way:

	$ export DOCKER_HOST="tcp://127.0.0.1:2375"
	$ export SECRET_KEY="secret"
	$ export CALLBACK_URL="http://dev:5000/docker_callback/"
	$ python app.py

Docker way:

	$ docker run \
	$ 	-v /var/run/docker.sock:/tmp/docker.sock \
	$	-e SECRET_KEY="secret" \
	$	-e CALLBACK_URL="http://dev:5000/docker_callback"
	$ 	mpapierski/eventspout

## Using eventspout

It is very transparent solution and does not need much configuration besides environment variables.

## Callbacks

Example callback:

	{
		"docker_host": "tcp://127.0.0.1:2375",
		"secret_key": "123",
		"event": {
			"id": "...",
			"status": "die",
			"from": "ubuntu:latest"
		}
	}

You should return "201" as success. Returning any other HTTP code will make `eventspout` transmission retry.

## LICENSE

MIT

## Author

Michał Papierski <michal@papierski.net>
