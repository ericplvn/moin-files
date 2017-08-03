all:
	docker build -t moin .

all-no-cache:
	docker build --no-cache -t moin .

run:
	docker run -ti --rm \
		-p 9111:9000 \
		-e WIKIUID=1000 \
		-e WIKIGID=1000 \
		-v /srv/wiki/:/srv/wiki \
		moin

run-bash:
	docker run -ti --rm \
		-p 9111:9000 \
		-e WIKIUID=1000 \
		-e WIKIGID=1000 \
		-v /srv/wiki/:/srv/wiki \
		--entrypoint="/bin/bash" \
		moin

