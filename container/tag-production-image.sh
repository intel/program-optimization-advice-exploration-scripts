#!/bin/bash
# Tag an image in gitlab.com to be production image used by default
# Usage: tag-production-image.sh [ <tag-name> ]
# If tag name provided, use that; otherwise tag development image to be production.

IMG_URL="registry.gitlab.com/davidwong/qaas"
tag_img="${IMG_URL}:development"
prod_img="${IMG_URL}:production"
if [[ $# == 1 ]]; then
	tag_img="${IMG_URL}:${1}"
fi


# login only need to be done once for password entering
docker login registry.gitlab.com
docker pull ${tag_img}
if [[ -z $( docker images -q ${tag_img}) ]]; then
	echo "Image: ${tag_img} not found.  Aborting..."
	exit 1
fi
echo tagging ${tag_img} to ${prod_img}
docker tag ${tag_img} ${prod_img}
docker push ${prod_img}
