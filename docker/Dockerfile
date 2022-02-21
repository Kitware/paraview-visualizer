FROM kitware/trame:1.2-glvnd-runtime-ubuntu20.04-py39

# Create the /deploy directory with trame-user as the owner
RUN install -d -o trame-user -g trame-user /deploy

# Install ParaView-EGL
ARG PV_URL=https://www.paraview.org/files/v5.10/ParaView-5.10.0-egl-MPI-Linux-Python3.9-x86_64.tar.gz
RUN mkdir -p /opt/paraview && cd /opt/paraview && wget -qO- $PV_URL | tar --strip-components=1 -xzv

# Needed for PV 5.10.0 but not in 5.10.1
COPY ./setup/trame.py /opt/paraview/lib/python3.9/site-packages/paraview/apps/

ENV PV_PYTHON /opt/paraview/bin/pvpython

# Copy the server directory
COPY --chown=trame-user:trame-user ./server /deploy/server
