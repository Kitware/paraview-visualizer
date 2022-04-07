## Building paraview-visualizer docker image (Linux only)

```bash
export TRAME_PARAVIEW=/path/to/your/paraview/home
./docker/scripts/build_image.sh
```

## Running your bundle

`./docker/scripts/run_image.sh` and open your browser to `http://localhost:8080/` or if you want to customize the starting directory `http://localhost:8080/?name=Visualizer&data=/data/sub-path-from-your-$home`