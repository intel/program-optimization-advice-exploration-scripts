#!/bin/bash
# Push current development image to gitlab.com and ensure there is a meaningful tag name
# Usage: push-image.sh <meaningful tag name>

if [[ $# != 1 ]]; then
	echo "Usage: $0 <meaningful tag name>"
	exit 1
fi
tag_name="$1"

IMG_URL="registry.gitlab.com/davidwong/qaas"
dev_img="${IMG_URL}:development"
tag_img="${IMG_URL}:${tag_name}"

if [[ -z $( docker images -q ${dev_img}) ]]; then
	echo "No development tag is found.  Aborting..."
	exit 1
fi

docker tag ${dev_img} ${tag_img}
if [[ $? != 0 ]]; then
        echo "Error in tagging development image as ${tag_img}.  Aborting..."
	exit 1
fi

# login only need to be done once for password entering
docker login registry.gitlab.com
docker push ${dev_img}
docker push ${tag_img}
