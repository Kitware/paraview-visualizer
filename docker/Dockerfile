FROM kitware/trame:1.2-glvnd-runtime-ubuntu20.04-py39

# Create the /deploy directory with trame-user as the owner
RUN install -d -o trame-user -g trame-user /deploy

# Install ParaView-EGL
# ARG PV_URL=https://www.paraview.org/files/v5.10/ParaView-5.10.0-egl-MPI-Linux-Python3.9-x86_64.tar.gz
ARG PV_URL=https://www.paraview.org/files/nightly/ParaView-master-5.10.1-1278-g070ee00d18-egl-MPI-Linux-Python3.9-x86_64.tar.gz
RUN mkdir -p /opt/paraview && cd /opt/paraview && wget -qO- $PV_URL | tar --strip-components=1 -xzv
ENV TRAME_PARAVIEW=/opt/paraview

# Copy the server directory
COPY --chown=trame-user:trame-user ./server /deploy/server
