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
Generally, there are two major image tags
- `qaas:development` : Most recent image under development
- `qaas:production` : Stable production image to be used by general users
- `qaas:`_other-tag_ : Other versions of image previously created

Following are some regular steps in container image development
1. Build updated image (as `qaas:development`)
   - Update `Dockerfile`
   - `./build-image.sh`
   - new image created locally but not pushed to Git Lab yet
2. Push development image to Git Lab
   - `./push-image.sh` _meaningful tag name_
   - Git Lab will receive the qaas:development image and also tagged it as qaas:_meaningful tag name_
3. Tag an image as production image (`qaas:production`)
   - `./tag-production-image.sh` [ _tag-name_ ]
   - _tag-name_ is optional.
     - if provided, tag that as `qaas:production` image
     - if not provided, tag `qaas:development` as `qaas:production`
