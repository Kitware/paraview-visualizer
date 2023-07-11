FROM kitware/trame:1.2-glvnd-runtime-ubuntu20.04-py39
COPY --chown=trame-user:trame-user .deploy-release/setup /deploy/setup
RUN /opt/trame/entrypoint.sh build

ENV TRAME_PARAVIEW=/opt/paraview