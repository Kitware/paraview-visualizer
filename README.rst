==========
Visualizer
==========

.. image:: https://github.com/Kitware/paraview-visualizer/actions/workflows/test_and_release.yml/badge.svg
    :target: https://github.com/Kitware/paraview-visualizer/actions/workflows/test_and_release.yml
    :alt: Test and Release

Visualizer is a Web frontend to ParaView based on trame. The current project is currently incomplete.
You can see it as an alpha version of what it could be. To make it fully functional we need more time and possibly funding.
But rather than waiting for it to be ready to release it, we are putting it out there as it does provide some very good example of what can be done with ParaView and trame.

If you would like us to push it forward or want some help creating something similar, feel free to reach out to `kitware <https://www.kitware.com/contact/>`_ so we can see how we can help you.

|image_1| |image_2| |image_3|

.. |image_1| image:: https://raw.githubusercontent.com/Kitware/paraview-visualizer/master/documentation/gallery/pv_visualizer_00.jpg
  :width: 30%
.. |image_2| image:: https://raw.githubusercontent.com/Kitware/paraview-visualizer/master/documentation/gallery/pv_visualizer_01.jpg
  :width: 30%
.. |image_3| image:: https://raw.githubusercontent.com/Kitware/paraview-visualizer/master/documentation/gallery/pv_visualizer_02.jpg
  :width: 30%


License
-------

This software is distributed under a BSD-3 license


Installing for Development
--------------------------

Build and install the Vue components

.. code-block:: console

    export NODE_OPTIONS=--openssl-legacy-provider
    cd vue-components
    npm i
    npm run build
    cd -

Create a virtual environment to use with your `ParaView 5.10+ <https://www.paraview.org/download/>`_

.. code-block:: console

    python3.9 -m venv .venv
    source .venv/bin/activate
    python -m pip install -U pip
    pip install -e .

Installing from release
-----------------------

Create a virtual environment to use with your `ParaView 5.10+ <https://www.paraview.org/download/>`_

.. code-block:: console

    python3.9 -m venv .venv
    source .venv/bin/activate
    python -m pip install -U pip pv-visualizer

Running the application
-----------------------

Run the application using `ParaView: pvpython <https://www.paraview.org/>`_ executable

.. code-block:: console

    export PVPYTHON=/Applications/ParaView-5.10.0.app/Contents/bin/pvpython # Using macOS install path as example
    export PV_VENV=$PWD/.venv
    export TRAME_APP=pv_visualizer.app

    $PVPYTHON -m paraview.apps.trame --data ~

Or you can use command line arguments instead of environment variables

.. code-block:: console

    $PVPYTHON -m paraview.apps.trame \
        --venv $PWD/.venv \
        --trame-app pv_visualizer.app \
        --data ~
