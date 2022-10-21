# QaaS Scripts
Scripts for QaaS infrastructure

## Installation
- Build local image
  - `cd container`
  - `./build-local-image.sh`

## Run QaaS Scripts
- Start container
  - `cd container`
  - `./run-container.sh` 
- Run Demo script
  - `cd ../scripts`
  - `python demo.py`
## Container maintance (under `container` directory)
Generally, there are two special image tags (`qaas:development` and `qaas:production`).
- `qaas:development` : Most recent image under development
- `qaas:production` : Stable production image to be used by general users.  By default `build-local-image.sh` builds local image using this image.

We also require all images to be tagged with some name meaningful to QaaS image development.
- `qaas:`_other-tag_ : _other-tag_ should provide some idea what the image is about.

Following are some regular steps in container image development
1. Build updated image (as `qaas:development`)
   1. Update `Dockerfile`
   2. `./build-image.sh`
   3. new image created locally but not pushed to Git Lab yet
2. Push development image to Git Lab
   1. `./push-image.sh` _tag-name_
   2. Git Lab will receive the `qaas:development` image and also tagged it as `qaas:`_tag-name_
3. Tag an image as production image (`qaas:production`)
   1. `./tag-production-image.sh` [ _tag-name_ ]
   2. _tag-name_ is optional.
      - if provided, tag `qaas:`_tag-name_ as `qaas:production` image
      - if not provided, tag `qaas:development` as `qaas:production`
