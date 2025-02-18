Backplane Scripts
=================

Installation
-------------------------
1. Follow [Backplane script document](../doc/HOWTO_BACKPLANE.md) for container-less installation instructions
   - Manual installation of dependencies and configuration
2. Follow [topmost installation instruction](../README.md)
   - The topmost setup.sh script will run setup.sh script of backplane to do the following automatically
     - Start a persistent container

Using Backplane outside container
--------------------------------
- Follow backplane script instruction for testing.
   - See [Backplane script document](../doc/HOWTO_BACKPLANE.md).

Using Backplane inside container
--------------------------------
1. Run/enter the backplane container
   - `../container/run-container.sh -i local_image_qaas_backplane:latest `
2. Follow backplane script instruction for testing.
   - See [Backplane script document](../doc/HOWTO_BACKPLANE.md).
