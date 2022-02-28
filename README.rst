==========
Visualizer
==========

Web frontend to ParaView

|image_1| |image_2| |image_3|

.. |image_1| image:: https://raw.githubusercontent.com/Kitware/paraview-visualizer/master/documentation/gallery/pv_visualizer_00.jpg
  :width: 30%
.. |image_2| image:: https://raw.githubusercontent.com/Kitware/paraview-visualizer/master/documentation/gallery/pv_visualizer_01.jpg
  :width: 30%
.. |image_3| image:: https://raw.githubusercontent.com/Kitware/paraview-visualizer/master/documentation/gallery/pv_visualizer_02.jpg
  :width: 30%


* Free software: BSD license


Development
------------
Build and install the Vue components

.. code-block:: console

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

Run the application using `ParaView: pvpython <https://www.paraview.org/>`_ executable

.. code-block:: console

    export PV_VENV=$PWD/.venv
    /Applications/ParaView-5.10.0.app/Contents/bin/pvpython \ # Using macOS install path as example
        pv_run.py \
        --data ~   \
        --server --dev


Run application
----------------

Create a virtual environment to use with your `ParaView 5.10.1+ <https://www.paraview.org/download/>`_

.. code-block:: console

    python3.9 -m venv .venv
    source .venv/bin/activate
    python -m pip install -U pip
    pip install pv-visualizer

Run the application using `ParaView: pvpython <https://www.paraview.org/>`_ executable with environment variables:

.. code-block:: console

    export PV_VENV=$PWD/.venv
    export TRAME_APP=pv_visualizer
    pvpython -m paraview.apps.trame --data ~


Or with command line arguments:

.. code-block:: console

    pvpython -m paraview.apps.trame \
        --venv $PWD/.venv \
        --trame-app pv_visualizer \
        --data ~
