all:
	docker build -t moindev .

all-no-cache:
	docker build --no-cache -t moin .

run:
	docker run -ti --rm \
		-p 9112:9000 \
		-e WIKIUID=1000 \
		-e WIKIGID=999 \
		-v /media/sf_WinShare/wiki-dev/:/srv/wiki \
		moindev

run-bash:
	docker run -ti --rm \
		-p 9112:9000 \
		-e WIKIUID=1000 \
		-e WIKIGID=999 \
		-v /media/sf_WinShare/wiki-dev/:/srv/wiki \
		--entrypoint="/bin/bash" \
		moindev

